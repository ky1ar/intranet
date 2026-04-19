import logging, os, re, math, uuid
import pandas as pd
from io import BytesIO
from datetime import datetime, timedelta, date
from werkzeug.utils import secure_filename
from application.handlers import handle_exceptions
from application.utils import parse_date_iso, parse_time, format_name, format_datetime, format_date, peru_time, upload_path, file_extension, allowed_extension
from application.services.push_service import PushSender
from application.services.module_service import ModuleService
from application.repository.attendance_repository import AttendanceRepository
from application.repository.user_repository import UserRepository
from application.repository.salary_repository import SalaryRepository
from application import socketio
from config import Paths
from flask_jwt_extended import get_jwt_identity


_RE_DATE_RANGE = re.compile(r"(\d{4}-\d{2}-\d{2})\s*~\s*(\d{4}-\d{2}-\d{2})")
_RE_TIME = re.compile(r"\d{2}:\d{2}")
_RE_DNI = re.compile(r"\d{8}")


class AttendanceService:
    def __init__(self):
        self.salary_repository = SalaryRepository()
        self.attendance_repository = AttendanceRepository()
        self.user_repository = UserRepository()
        self.push_service = PushSender()
        self.module_service = ModuleService()
        self.management_dep = 7
        self.worker_lvl = 2
        self.leader_lvl = 3
        self.admin_lvl = 4


    def _has_perm(self, user_id, perm_slug):
        result, code = self.module_service.check_permission(user_id, 'attendance', perm_slug)
        if code != 200:
            return False
        return result.get('granted', False) if isinstance(result, dict) else False


    def _can_see_department(self, user_id, department_slug):
        """Verifica si el usuario puede ver un departamento específico"""
        if not department_slug:
            return False
        if self._has_perm(user_id, 'view_all'):
            return True
        return self._has_perm(user_id, f'view_{department_slug}')


    def _get_visible_user_ids(self, user_id):
        """Retorna todos los user_ids que este usuario puede ver"""
        if self._has_perm(user_id, 'view_all'):
            all_ids, rc = self.user_repository.get_all_user_ids()
            return all_ids if rc == 200 else [user_id]

        # Leer permisos view_* del módulo
        modules_data, _ = self.module_service.get_user_modules(user_id)
        dept_slugs = []
        if isinstance(modules_data, list):
            for m in modules_data:
                if m['slug'] == 'attendance':
                    for perm_slug, granted in m.get('permissions', {}).items():
                        if granted and perm_slug.startswith('view_'):
                            dept_slugs.append(perm_slug.replace('view_', ''))
                    break

        if dept_slugs:
            area_ids, rc = self.user_repository.get_user_ids_by_department_slugs(dept_slugs)
            if rc == 200:
                visible = set(area_ids)
                visible.add(user_id)
                visible.discard(23)
                return list(visible)

        return [user_id]


    def _adj_priority(self, scope):
        return {"all": 0, "department": 1, "profile": 2, "user": 3}.get(scope or "all", 0)


    def _build_adjustments_map(self, adjustments_rows):
        mp = {}
        for a in (adjustments_rows or []):
            key = a.date.isoformat()
            mp.setdefault(key, []).append(a)
        return mp
    

    def _hhmm_to_minutes(self, hhmm):
        hh, mm = hhmm.split(":")
        return int(hh) * 60 + int(mm)


    def _expected_start_minutes_for_date(self, profile_map, d: date):
        wd = d.weekday()
        starts = [a for (a, b) in (profile_map.get(wd) or [])]
        return min(starts) if starts else None


    def _minutes_to_hhmm(self, mins: int):
        hh = mins // 60
        mm = mins % 60
        return f"{hh:02d}:{mm:02d}"


    def _time_to_minutes(self, t):
        return int(t.hour) * 60 + int(t.minute)


    def _interval_minutes(self, it: dict):
        if not it or not it.get("start") or not it.get("end"):
            return 0
        return max(0, self._hhmm_to_minutes(it["end"]) - self._hhmm_to_minutes(it["start"]))


    def _build_profile_map(self, shifts_rows):
        mp = {i: [] for i in range(7)}
        for s in shifts_rows:
            mp[int(s.weekday)].append((self._time_to_minutes(s.start_time), self._time_to_minutes(s.end_time)))
        return mp


    def _target_minutes_for_date(self, profile_map, d: date):
        wd = d.weekday()
        total = 0
        for a, b in (profile_map.get(wd) or []):
            total += max(0, b - a)
        return total

        
    def _first_day_next_month(self, d):
        y, m = d.year, d.month
        if m == 12:
            return date(y + 1, 1, 1)
        return date(y, m + 1, 1)


    def _daynum_to_date(self, day_num: int, period_start: date) -> date:
        base = period_start.replace(day=1)
        d = base + timedelta(days=day_num - 1)

        if d < period_start:
            next_base = self._first_day_next_month(base)
            d = next_base + timedelta(days=day_num - 1)

        return d


    def _normalize_times(self, times, window_minutes=5):
        out = []
        last_min = None

        for t in times:
            t = (t or "").strip()
            if not t:
                continue

            try:
                cur = self._hhmm_to_minutes(t)
            except Exception:
                continue

            if not out:
                out.append(t)
                last_min = cur
                continue

            delta = cur - last_min
            if 0 <= delta <= window_minutes:
                continue

            out.append(t)
            last_min = cur

        return out


    def _row_is_empty(self, row):
        return all((str(c).strip() == "" for c in row))


    def _extract_period(self, rows):
        for r in rows[:40]:
            for c in r:
                m = _RE_DATE_RANGE.search(str(c))
                if m:
                    return {"start": m.group(1), "end": m.group(2)}
        return None


    def _find_days_row(self, rows):
        best_idx = None
        best_nums = None
        best_len = 0

        for idx, r in enumerate(rows[:120]):
            nums = []
            for c in r:
                s = str(c).strip()
                if s.isdigit():
                    n = int(s)
                    if 1 <= n <= 31:
                        nums.append(n)

            if len(nums) >= 2 and len(nums) > best_len:
                best_idx = idx
                best_nums = nums
                best_len = len(nums)

        return best_idx, best_nums


    def _looks_like_user_header(self, row):
        srow = " ".join(str(x) for x in row)
        return ("ID:" in srow) and ("Nombre:" in srow) and ("Departamento:" in srow)


    def _value_after_label(self, row, label, want="text"):
        for i, cell in enumerate(row):
            if str(cell).strip() == label:
                for j in range(i + 1, min(i + 12, len(row))):
                    v = str(row[j]).strip()
                    if not v:
                        continue
                    if want == "dni":
                        m = _RE_DNI.search(v)
                        if m:
                            return m.group(0)
                        continue
                    if v.endswith(":") and len(v) <= 25:
                        continue
                    return v
        return ""


    def _parse_user_header(self, row):
        dni = self._value_after_label(row, "ID:", want="dni")
        if not dni:
            m = _RE_DNI.search(" ".join(str(x) for x in row))
            dni = m.group(0) if m else ""

        return {
            "dni": (dni or "").strip(),
        }


    def _parse_schedule_row(self, row, days, period_start):
        if not row or not days:
            return {}

        n = min(len(days), len(row))
        marks = {}

        for col_idx in range(n):
            cell = str(row[col_idx] or "").strip()
            if not cell:
                continue

            times = self._extract_times(cell)
            if not times:
                continue

            day_num = int(days[col_idx])
            d = self._daynum_to_date(day_num, period_start)

            marks[d.isoformat()] = times

        return marks


    def _extract_times(self, cell):
        raw = _RE_TIME.findall(cell or "")
        compact = []
        for t in raw:
            if not compact or compact[-1] != t:
                compact.append(t)

        return self._normalize_times(compact, window_minutes=10)


    @handle_exceptions
    def xls_process(self, file, file_bytes):
        ext = (os.path.splitext(file.filename)[1] or "").lower()
        if ext not in {".xls", ".xlsx"}:
            return f"Invalid file type: {ext}. Use .xls or .xlsx", 400

        engine = "openpyxl" if ext == ".xlsx" else "xlrd"

        try:
            df = pd.read_excel(
                BytesIO(file_bytes),
                sheet_name="Reporte de Asistencia",
                engine=engine,
                header=None,
                dtype=str,
            ).fillna("")
        except ValueError as e:
            return str(e), 400
        except Exception as e:
            return f"Could not read Excel file: {e}", 400

        rows = df.values.tolist()

        logging.info(rows)
        period = self._extract_period(rows)
        if not period:
            return "Could not find period 'YYYY-MM-DD ~ YYYY-MM-DD'", 400

        days_row_idx, days = self._find_days_row(rows)
        if days_row_idx is None:
            return "Could not find days row (1..N)", 400

        start_date = datetime.strptime(period["start"], "%Y-%m-%d").date()

        users = []
        i = days_row_idx + 1

        while i < len(rows):
            if self._row_is_empty(rows[i]):
                i += 1
                continue

            if self._looks_like_user_header(rows[i]):
                user = self._parse_user_header(rows[i])
                sched_row = rows[i + 1] if i + 1 < len(rows) else []
                marks = self._parse_schedule_row(sched_row, days, start_date)

                if marks:
                    user["marks"] = marks
                    users.append(user)

                i += 2
                continue

            i += 1

        raw_rows = []
        for u in users:
            dni = (u.get("dni") or "").strip()
            for date_iso, times in (u.get("marks") or {}).items():
                for hhmm in (times or []):
                    hhmm = (hhmm or "").strip()
                    if dni and date_iso and hhmm:
                        raw_rows.append((dni, date_iso, hhmm))

        if not raw_rows:
            return {
                "period": period,
                "inserted": 0,
                "skipped_duplicates": 0,
                "missing_clients": [],
            }, 200

        dni_to_user_id = {}
        missing_clients = []

        for dni, _, _ in raw_rows:
            if dni in dni_to_user_id:
                continue

            user_id, uc = self.user_repository.get_user_by_document(dni)
            if uc != 200:
                missing_clients.append(dni)
                continue

            dni_to_user_id[dni] = int(user_id.id)

        marks_rows = []
        for dni, date_iso, hhmm in raw_rows:
            user_id = dni_to_user_id.get(dni)
            if not user_id:
                continue

            d = parse_date_iso(date_iso)
            t = parse_time(hhmm)

            marks_rows.append({
                "user_id": user_id,
                "date": d,
                "mark_at": t,
            })

        res, rc = self.attendance_repository.save_marks(marks_rows)
        if rc != 200:
            return res, rc

        return {
            "period": period,
            "inserted": res.get("inserted", 0),
            "skipped_duplicates": res.get("skipped_duplicates", 0),
            "missing_clients": sorted(set(missing_clients)),
        }, 200
    

    @handle_exceptions
    def duration(self):
        durations, dc = self.attendance_repository.get_durations() 
        if dc != 200:
            return durations, dc
        
        result = [
            {
                "id": duration.id,
                "name": duration.name,
            }
            for duration in durations
        ]
        return result, 200


    @handle_exceptions
    def leave(self):
        leaves, dc = self.attendance_repository.get_leaves() 
        if dc != 200:
            return leaves, dc
        
        result = [
            {
                "id": leave.id,
                "name": leave.name,
            }
            for leave in leaves
        ]
        return result, 200


    @handle_exceptions
    def leave_requests(self):
        user_id = int(get_jwt_identity())
        user, uc = self.user_repository.get_user_by_id(user_id)
        if uc != 200:
            return user, uc

        visible_user_ids = self._get_visible_user_ids(user_id)

        leave_requests, lrc = self.attendance_repository.get_leave_requests(visible_user_ids)
        if lrc != 200:
            return leave_requests, lrc

        return self._format_requests_reponse(leave_requests, user_id)
    

    @handle_exceptions
    def _format_requests_reponse(self, leave_requests, user_id):
        return {
            "requests": [
                {
                    "id": leave.id,
                    "requester_name": format_name(leave.user.name) if user_id != leave.user_id else 'Tú',
                    "requester_image": leave.user.image,
                    "requester_department": leave.user.department.name,
                    "request_type": leave.request_type,
                    "status_name": leave.status.name,
                    "status_slug": leave.status.slug,
                } for leave in leave_requests
            ],
        }, 200


    def _adjustment_best_for_date(self, profile_map, d: date, user, profile, adjustments_map):
        default_target = self._target_minutes_for_date(profile_map, d)
        if default_target <= 0:
            return []

        candidates = (adjustments_map.get(d.isoformat()) or [])
        if not candidates:
            return []

        applicable = []
        for a in candidates:
            scope = (a.scope or "all").lower().strip()

            if scope == "all":
                applicable.append(a)
                continue

            if scope == "department":
                if a.department_id is not None and int(a.department_id) == int(user.department_id):
                    applicable.append(a)
                continue

            if scope == "profile":
                if a.profile_id is not None and int(a.profile_id) == int(profile.id):
                    applicable.append(a)
                continue

            if scope == "user":
                if a.user_id is not None and int(a.user_id) == int(user.id):
                    applicable.append(a)
                continue

        if not applicable:
            return []

        best_p = max(self._adj_priority(a.scope) for a in applicable)
        best = [a for a in applicable if self._adj_priority(a.scope) == best_p]

        best.sort(key=lambda x: self._time_to_minutes(x.start_time))
        return best


    def _adjustment_marks_for_date(self, profile_map, d: date, user, profile, adjustments_map) -> int:
        best = self._adjustment_best_for_date(profile_map, d, user, profile, adjustments_map)
        return len(best) * 2


    def _adjustment_best_items_for_date(self, profile_map, d, user, profile, adjustments_map):
        default_target = self._target_minutes_for_date(profile_map, d)
        if default_target <= 0:
            return []

        candidates = (adjustments_map.get(d.isoformat()) or [])
        if not candidates:
            return []

        applicable = []
        for a in candidates:
            scope = (a.scope or "all").lower().strip()

            if scope == "all":
                applicable.append(a)
                continue

            if scope == "department":
                if a.department_id is not None and int(a.department_id) == int(user.department_id):
                    applicable.append(a)
                continue

            if scope == "profile":
                if a.profile_id is not None and int(a.profile_id) == int(profile.id):
                    applicable.append(a)
                continue

            if scope == "user":
                if a.user_id is not None and int(a.user_id) == int(user.id):
                    applicable.append(a)
                continue

        if not applicable:
            return []

        best_p = max(self._adj_priority(a.scope) for a in applicable)
        best = [a for a in applicable if self._adj_priority(a.scope) == best_p]
        best.sort(key=lambda x: (x.start_time.hour, x.start_time.minute))

        _re_leave_id = re.compile(r" - LI-(\d+)$")
        items = []
        for a in best:
            s = self._minutes_to_hhmm(self._time_to_minutes(a.start_time))
            e = self._minutes_to_hhmm(self._time_to_minutes(a.end_time))
            label = (a.description or "").strip() or "Ajuste"
            m = _re_leave_id.search(label)
            leave_id = int(m.group(1)) if m else None
            items.append({
                "label": label,
                "value": f"{s} - {e}",
                "leave_id": leave_id,
            })

        return items


    @handle_exceptions
    def summary_by_offset(self, data):
        user_id = int(data.get("user_id"))
        offset = int(data.get("offset") or 0)

        period, pc = self.attendance_repository.get_period_by_offset(offset, today=date.today())
        if pc != 200:
            return period, pc

        if not period:
            return {"period": None, "weeks": []}, 200

        logging.info(f"Periodo: {period.name}, offset calculado: {offset}")
        payload, rc = self.attendance_repository.build_period_summary(user_id, period)
        if rc != 200:
            return payload, rc

        start_in_period, sic = self.attendance_repository.get_user_profile_start_in_period(user_id, period.start_date, period.end_date)
        if sic != 200:
            return start_in_period, sic

        if not start_in_period:
            return {
                **payload,
                "profile": None,
                "profile_error": "Usuario sin perfil asignado en este período (user_work_profile)",
            }, 200

        leave_adjustment, _ = self.attendance_repository.get_user_leave_adjustment(user_id)
        if leave_adjustment:
            payload["finish_date"] = leave_adjustment.finish_date

        # Usar leave_balance para available_leave (con fallback a leave_adjustment)
        leave_bal, lbc = self.attendance_repository.get_leave_balance(user_id, period.id)
        if leave_bal:
            payload["available_leave"] = float(leave_bal.balance)
        elif leave_adjustment:
            payload["available_leave"] = int(leave_adjustment.available)
            
        effective_start = max(period.start_date, start_in_period)
        payload["effective_start_date"] = effective_start.isoformat()

        profile, prc = self.attendance_repository.get_profile_for_user_on_date(user_id, effective_start)
        if prc != 200:
            return profile, prc

        if not profile:
            return {
                **payload,
                "profile": None,
                "profile_error": "Usuario sin perfil asignado (user_work_profile)",
            }, 200

        shifts, src = self.attendance_repository.get_shifts_for_profile(profile.id)
        if src != 200:
            return shifts, src

        profile_map = self._build_profile_map(shifts)

        user, uc = self.user_repository.get_user_by_id(user_id)
        if uc != 200:
            return user, uc

        adjs, ac = self.attendance_repository.get_adjustments_by_range(period.start_date, period.end_date)
        if ac != 200:
            return adjs, ac
        adjustments_map = self._build_adjustments_map(adjs)

        for w in payload.get("weeks", []):
            week_worked = 0
            week_target = 0
            week_incomplete = 0

            for day in w.get("days", []):
                dt = parse_date_iso(day["date"])
                wd = dt.weekday()

                if day.get("in_period") and dt < effective_start:
                    target = self._target_minutes_for_date(profile_map, dt)
                    day["expected_marks"] = 0
                    day["expected_start"] = None
                    day["target_min"] = target
                    day["worked_min"] = 0
                    day["delta_min"] = 0 - target
                    day["incomplete"] = False
                    day["incomplete_count"] = 0
                    day["has_adjustment"] = False
                    day["adjustment_bonus_min"] = 0
                    day["adjustment_marks"] = 0
                    day["adjustment_items"] = []
                    day["not_started_yet"] = True
                    day["is_summary"] = False
                    week_target += target
                    continue

                if wd == 6:
                    day["is_summary"] = True
                    day["label"] = "Σ"
                    day["intervals"] = []
                    day["summary"] = {
                        "worked_min": week_worked,
                        "target_min": week_target,
                        "delta_min": week_worked - week_target,
                        "incomplete": week_incomplete,
                    }
                    continue

                day["is_summary"] = False

                shifts_for_day = (profile_map.get(wd) or [])
                day["expected_marks"] = len(shifts_for_day) * 2

                # ✅ aplica permiso si existe (antes de lateness / incomplete)
                if day.get("in_period") and day.get("is_permit"):
                    self._apply_permit_rules(day, shifts_for_day)
                    
                target = self._target_minutes_for_date(profile_map, dt)
                expected_start_min = self._expected_start_minutes_for_date(profile_map, dt)
                day["expected_start"] = (
                    self._minutes_to_hhmm(expected_start_min) if expected_start_min is not None else None
                )

                if day.get("in_period"):
                    week_target += target

                bonus_min = self._adjustment_bonus_minutes_for_date(
                    profile_map=profile_map,
                    d=dt,
                    user=user,
                    profile=profile,
                    adjustments_map=adjustments_map,
                )
                day["adjustment_bonus_min"] = bonus_min

                adj_marks = bonus_min // 120
                day["adjustment_marks"] = int(max(0, min(adj_marks, day["expected_marks"])))

                adj_items = self._adjustment_best_items_for_date(
                    profile_map=profile_map,
                    d=dt,
                    user=user,
                    profile=profile,
                    adjustments_map=adjustments_map,
                )
                day["adjustment_items"] = adj_items
                day["has_adjustment"] = len(adj_items) > 0

                if day.get("is_vacation") and day.get("in_period"):
                    day["intervals"] = []              # no mostrar marcaciones
                    day["expected_marks"] = 0          # no pedir marcaciones
                    day["expected_start"] = None
                    day["worked_min"] = target + bonus_min
                    day["target_min"] = target
                    day["delta_min"] = day["worked_min"] - target
                    day["incomplete"] = False
                    day["incomplete_count"] = 0

                    week_worked += day["worked_min"]
                    continue

                if day.get("is_holiday") and day.get("in_period"):
                    day["worked_min"] = target + bonus_min
                    day["target_min"] = target
                    day["delta_min"] = day["worked_min"] - target
                    day["incomplete"] = False
                    day["incomplete_count"] = 0

                    week_worked += day["worked_min"]
                    continue

                worked = 0
                has_open_interval = False

                for it in (day.get("intervals") or []):
                    if it.get("start") and not it.get("end"):
                        has_open_interval = True
                    worked += self._interval_minutes(it)

                worked += bonus_min

                day["target_min"] = target
                day["worked_min"] = worked
                day["incomplete"] = bool(has_open_interval)
                day["incomplete_count"] = 1 if has_open_interval else 0

                if has_open_interval:
                    day["delta_min"] = None
                    week_incomplete += 1
                    continue

                day["delta_min"] = worked - target
                week_worked += worked

        payload["profile"] = {"id": profile.id, "slug": profile.slug, "name": profile.name}
        return payload, 200


    @handle_exceptions
    def get_department_team(self, user_id):
        user, uc = self.user_repository.get_user_by_id(user_id)
        if uc != 200:
            return user, uc

        if user.level_id == 1:
            return "Usuario sin acceso al sistema", 400

        team, tc = self.user_repository.get_users_by_department(user.department_id)
        if tc != 200:
            return team, tc

        team_dict = [
            {
                "id": t.id,
                "level_id": t.level_id,
                "name": format_name(t.name),
                "department_name": t.department.name,
                "image": t.image if t.image else 'user_default.jpg',
            } for t in team
        ]

        return team_dict, 200
    

    def _adjustment_bonus_minutes_for_date(self, profile_map, d, user, profile, adjustments_map):
        default_target = self._target_minutes_for_date(profile_map, d)
        if default_target <= 0:
            return 0

        candidates = (adjustments_map.get(d.isoformat()) or [])
        if not candidates:
            return 0

        applicable = []
        for a in candidates:
            scope = (a.scope or "all").lower().strip()

            if scope == "all":
                applicable.append(a)
                continue

            if scope == "department":
                if a.department_id is not None and int(a.department_id) == int(user.department_id):
                    applicable.append(a)
                continue

            if scope == "profile":
                if a.profile_id is not None and int(a.profile_id) == int(profile.id):
                    applicable.append(a)
                continue

            if scope == "user":
                if a.user_id is not None and int(a.user_id) == int(user.id):
                    applicable.append(a)
                continue

        if not applicable:
            return 0

        best_p = max(self._adj_priority(a.scope) for a in applicable)
        best = [a for a in applicable if self._adj_priority(a.scope) == best_p]

        bonus = 0
        for a in best:
            bonus += max(0, self._time_to_minutes(a.end_time) - self._time_to_minutes(a.start_time))

        return bonus


    def _expected_marks_for_user_on_date(self, user_id, d):
        profile, prc = self.attendance_repository.get_profile_for_user_on_date(user_id, d)
        if prc != 200:
            raise Exception(profile)

        if not profile:
            return 0

        shifts, src = self.attendance_repository.get_shifts_for_profile(profile.id)
        if src != 200:
            raise Exception(shifts)

        profile_map = self._build_profile_map(shifts)
        wd = d.weekday()
        return len(profile_map.get(wd) or []) * 2


    @handle_exceptions
    def complete_marks(self, data):
        editor_user_id = int(get_jwt_identity())

        user_id = int(data.get("user_id"))
        d = parse_date_iso(data.get("date"))

        holiday, hc = self.attendance_repository.get_holiday_on_date(d)
        if hc != 200:
            return holiday, hc
        if holiday:
            return "No se puede completar marcaciones en un feriado.", 422

        existing, ec = self.attendance_repository.get_marks_by_user_and_date(user_id, d)
        if ec != 200:
            return existing, ec

        existing_times = [m.mark_at.strftime("%H:%M") for m in (existing or [])]

        expected_total = self._expected_marks_for_user_on_date(user_id, d)

        if expected_total <= 0:
            n = len(existing_times)
            if n > 0 and (n % 2 == 1):
                expected_manual = min(n + 1, 4)
            else:
                return "Este día no requiere marcaciones.", 422
        else:
            profile, prc = self.attendance_repository.get_profile_for_user_on_date(user_id, d)
            if prc != 200:
                return profile, prc
            if not profile:
                return "Usuario sin perfil asignado (user_work_profile)", 422

            shifts, src = self.attendance_repository.get_shifts_for_profile(profile.id)
            if src != 200:
                return shifts, src
            profile_map = self._build_profile_map(shifts)

            permits, pc = self.attendance_repository.get_permits_by_range(user_id, d, d)
            if pc != 200:
                return permits, pc

            permit = permits.get(d.isoformat())
            permit_reduce = 0
            if permit:
                duration_id = permit.get("duration_id")
                try:
                    duration_id = int(duration_id) if duration_id is not None else None
                except Exception:
                    duration_id = None

                shifts_for_day = sorted(profile_map.get(d.weekday()) or [], key=lambda x: x[0])
                covered = self._permit_covered_shift_indexes(shifts_for_day, duration_id) if duration_id else []
                permit_reduce = len(covered) * 2

            expected_total = max(0, expected_total - permit_reduce)

            user, uc = self.user_repository.get_user_by_id(user_id)
            if uc != 200:
                return user, uc

            adjs, ac = self.attendance_repository.get_adjustments_by_range(d, d)
            if ac != 200:
                return adjs, ac
            adjustments_map = self._build_adjustments_map(adjs)

            adj_marks = self._adjustment_marks_for_date(
                profile_map=profile_map,
                d=d,
                user=user,
                profile=profile,
                adjustments_map=adjustments_map,
            )

            expected_manual = max(0, expected_total - adj_marks)

            client_expected = data.get("expected_marks")
            if client_expected is not None:
                try:
                    client_expected = int(client_expected)
                except Exception:
                    return "expected_marks inválido.", 422

                if client_expected != expected_manual:
                    return f"expected_marks no coincide. Esperado: {expected_manual}.", 422

            if expected_manual <= 0:
                return "El día ya está completo.", 409

        if len(existing_times) >= expected_manual:
            return "El día ya está completo.", 409

        additions = data.get("additions") or []
        if not isinstance(additions, list):
            return "additions debe ser una lista.", 422

        add_positions = set()
        add_times = []
        for a in additions:
            if not isinstance(a, dict):
                return "Formato inválido en additions.", 422

            t = (a.get("time") or "").strip()
            pos = a.get("position")

            if not t or not isinstance(pos, int):
                return "Cada addition requiere time y position.", 422

            if pos < 0 or pos >= expected_manual:
                return f"position fuera de rango: {pos}.", 422

            try:
                parse_time(t)
            except Exception:
                return f"Hora inválida: {t}.", 422

            if pos in add_positions:
                return f"position repetido: {pos}.", 422
            add_positions.add(pos)

            add_times.append((pos, t))

        final = [None] * expected_manual

        for pos, t in add_times:
            final[pos] = t

        it = iter(existing_times)
        for i in range(expected_manual):
            if final[i] is None:
                try:
                    final[i] = next(it)
                except StopIteration:
                    break

        if any(x is None for x in final):
            return "No alcanza para completar el día con esos datos.", 422

        if len(set(final)) != len(final):
            return "No se permiten horas duplicadas.", 422

        mins = [self._hhmm_to_minutes(hhmm) for hhmm in final]
        if mins != sorted(mins):
            return "Las marcaciones deben quedar en orden cronológico.", 422

        existing_set = set(existing_times)
        to_insert = []
        for pos, hhmm in add_times:
            if hhmm in existing_set:
                return f"La hora {hhmm} ya existe en el día.", 422
            to_insert.append({
                "user_id": user_id,
                "date": d,
                "mark_at": parse_time(hhmm),
                "created_by": editor_user_id,
            })

        res, rc = self.attendance_repository.insert_marks_with_meta(to_insert)
        if rc != 200:
            return res, rc

        return {
            "message": "Marcaciones completadas.",
            "expected_marks": expected_manual,
            "inserted": res.get("inserted", 0),
            "final": final,
        }, 200
    

    @handle_exceptions
    def leave_request(self, data):
        user_id = int(data["user_id"])
        user, uc = self.user_repository.get_user_by_id(user_id)
        if uc != 200:
            return user, uc

        # Status inicial según permisos del creador
        if self._has_perm(user_id, 'approve_leave_manager'):
            # Gerencia: salta todo → aprobado directo
            data["_initial_status"] = 4
        elif self._has_perm(user_id, 'approve_leave_rrhh'):
            # RRHH: salta área y RRHH → espera gerencia
            data["_initial_status"] = 3
        elif self._has_perm(user_id, 'approve_leave'):
            # Líder de área: salta área → espera RRHH
            data["_initial_status"] = 2
        else:
            # Worker: pendiente → espera área
            data["_initial_status"] = 1

        start_date = parse_date_iso(data.get("start_date"))
        data["start_date"] = start_date

        end_date = data.get("end_date")
        data["end_date"] = parse_date_iso(end_date) if end_date else start_date

        res, rc = self.attendance_repository.insert_leave_request(data)
        if rc != 200:
            return res, rc

        leave_id = res.get("id")

        # Notificaciones según status inicial
        # TODO: notificar al nivel siguiente
        
        socketio.emit("attendance_update_leaves", {})
        return "Solicitud procesada correctamente.", 200
    

    @handle_exceptions
    def get_leave(self, leave_id):
        leave, pc = self.attendance_repository.get_leave_by_id(leave_id)
        if pc != 200:
            return leave, pc

        user_id = int(get_jwt_identity())
        user, uc = self.user_repository.get_user_by_id(user_id)
        if uc != 200:
            return user, uc

        status_id = leave.status_id
        is_owner = (user_id == leave.user_id)

        can_approve      = self._has_perm(user_id, 'approve_leave')
        can_approve_rrhh = self._has_perm(user_id, 'approve_leave_rrhh')
        can_approve_mgr  = self._has_perm(user_id, 'approve_leave_manager')

        # ¿Puede ver el área del creador?
        creator_dept_slug = leave.user.department.slug if leave.user.department else None
        can_see_creator = self._can_see_department(user_id, creator_dept_slug)

        # Determinar modal
        if status_id == 1:
            if can_approve and can_see_creator:
                modal = "approve"
            elif is_owner:
                modal = "edit"
            else:
                modal = "view"

        elif status_id == 2:
            if can_approve_rrhh:
                modal = "approve"
            elif is_owner:
                modal = "view"
            else:
                modal = "view"

        elif status_id == 3:
            if can_approve_mgr:
                modal = "approve"
            else:
                modal = "view"

        else:
            modal = "view"

        dto = {
            "id": leave.id,
            "modal": modal,
            "type": ('permit' if leave.request_type == 'Permiso'
                     else 'medical' if leave.request_type == 'Descanso Médico'
                     else 'vacation'),
            "user_name": format_name(leave.user.name),
            "request_type": leave.request_type,
            "status_id": status_id,
            "status_slug": leave.status.slug,
            "status_name": leave.status.name,
            "start_date": leave.start_date.isoformat(),
            "start_date_text": format_date(leave.start_date),
            "end_date": leave.end_date.isoformat(),
            "end_date_text": format_date(leave.end_date),
            "duration_id": leave.duration_id,
            "duration_name": leave.duration.name if leave.duration_id else None,
            "leave_type": leave.type.name if leave.leave_type_id else None,
            "leave_type_id": leave.leave_type_id,
            "leave_type_detail": leave.leave_type_detail,
            "description": leave.description,
            "motive": leave.motive,
            "recovery_plan": leave.recovery_plan,
            "assigned_name": format_name(leave.assigned.name) if leave.assigned_user_id else None,
            "assigned_id": leave.assigned_user_id,
            "self_created": is_owner,
            "created_at": format_datetime(leave.created_at),
        }

        return dto, 200


    @handle_exceptions
    def leave_update(self, data):
        user_id = int(get_jwt_identity())
        user, uc = self.user_repository.get_user_by_id(user_id)
        if uc != 200:
            return user, uc

        action = data.get("action")
        leave_id = data.get("leave_id")
        user_name = user.name

        # ── DELETE ─────────────────────────────────────────────────
        if data.get("delete") is True:
            delete, dc = self.attendance_repository.soft_delete(leave_id)
            if dc != 200:
                return delete, dc

        # ── APPROVE ────────────────────────────────────────────────
        elif action == "approve":
            can_approve      = self._has_perm(user_id, 'approve_leave')
            can_approve_rrhh = self._has_perm(user_id, 'approve_leave_rrhh')
            can_approve_mgr  = self._has_perm(user_id, 'approve_leave_manager')

            leave, lc = self.attendance_repository.get_leave_by_id(leave_id)
            if lc != 200:
                return leave, lc

            current_status = leave.status_id
            creator_id = leave.user_id
            creator_name = leave.user.name
            creator_dept_slug = leave.user.department.slug if leave.user.department else None
            is_permit = leave.request_type == 'Permiso'

            new_status = None

            if current_status == 1 and can_approve:
                if not self._can_see_department(user_id, creator_dept_slug):
                    return "No tienes acceso a esta área", 403
                new_status = 2

            elif current_status == 2 and can_approve_rrhh:
                new_status = 3

            elif current_status == 3 and can_approve_mgr:
                new_status = 4

            else:
                return "No autorizado para aprobar en este nivel", 403

            status, sc = self.attendance_repository.set_status(leave_id, new_status)
            if sc != 200:
                return status, sc

            # ── Notificaciones ─────────────────────────────────────
            if new_status == 2:
                self.push_service.send_to_user(
                    user_id=creator_id,
                    title="Solicitud validada por área",
                    body=f"{format_name(user_name, True)} aprobó tu solicitud LI-{leave_id}. En espera de RRHH.",
                )

            elif new_status == 3:
                self.push_service.send_to_user(
                    user_id=creator_id,
                    title="Solicitud validada por RRHH",
                    body=f"Tu solicitud LI-{leave_id} fue aprobada por RRHH. En espera de Gerencia.",
                )

            elif new_status == 4:
                is_medical = leave.request_type == 'Descanso Médico'

                if is_medical:
                    title = "Descanso médico aprobado"
                    # Generar los attendance_day_adjustment
                    try:
                        self._create_adjustments_for_medical_leave(leave)
                    except Exception as ex:
                        logging.exception(f"Error creando adjustments para LI-{leave_id}: {ex}")
                elif is_permit:
                    title = "Permiso aprobado"
                else:
                    title = "Vacaciones aprobadas"

                self.push_service.send_to_user(
                    user_id=creator_id,
                    title=title,
                    body=f"Tu solicitud LI-{leave_id} ha sido aprobada.",
                )

        # ── REJECT ─────────────────────────────────────────────────
        elif action == "reject":
            can_approve      = self._has_perm(user_id, 'approve_leave')
            can_approve_rrhh = self._has_perm(user_id, 'approve_leave_rrhh')
            can_approve_mgr  = self._has_perm(user_id, 'approve_leave_manager')

            leave, lc = self.attendance_repository.get_leave_by_id(leave_id)
            if lc != 200:
                return leave, lc

            current_status = leave.status_id
            creator_id = leave.user_id
            creator_dept_slug = leave.user.department.slug if leave.user.department else None
            is_permit = leave.request_type == 'Permiso'

            can_reject = False
            reject_level = ""

            if current_status == 1 and can_approve:
                if self._can_see_department(user_id, creator_dept_slug):
                    can_reject = True
                    reject_level = "área"

            elif current_status == 2 and can_approve_rrhh:
                can_reject = True
                reject_level = "RRHH"

            elif current_status == 3 and can_approve_mgr:
                can_reject = True
                reject_level = "Gerencia"

            if not can_reject:
                return "No autorizado para rechazar en este nivel", 403

            result, code = self.attendance_repository.set_status(leave_id, status_id=5)
            if code != 200:
                return result, code

            is_medical = leave.request_type == 'Descanso Médico'
            if is_medical:
                title = "Descanso médico rechazado"
            elif is_permit:
                title = "Permiso rechazado"
            else:
                title = "Vacaciones rechazadas"

            self.push_service.send_to_user(
                user_id=creator_id,
                title=title,
                body=f"Tu solicitud LI-{leave.id} fue rechazada por {reject_level}.",
            )

        # ── EDIT (update fields) ───────────────────────────────────
        else:
            start_date = parse_date_iso(data.get("start_date"))
            data["start_date"] = start_date

            end_date = data.get("end_date")
            data["end_date"] = parse_date_iso(end_date) if end_date else start_date

            result, code = self.attendance_repository.update_leave(data)
            if code != 200:
                return result, code

        socketio.emit("attendance_update_leaves", {})
        return "Solicitud actualizada correctamente", 200
    

    def _permit_covered_shift_indexes(self, shifts_for_day, duration_id):
        if not shifts_for_day:
            return []

        n = len(shifts_for_day)
        if duration_id == 3:
            return list(range(n))          # todo el día
        if duration_id == 1:
            return [0]                     # mañana = primer shift
        if duration_id == 2:
            return [n - 1]                 # tarde = último shift
            
        return []
    

    def _apply_permit_rules(self, day, shifts_for_day):
        permit = day.get("permit") or {}
        if not permit:
            return

        duration_id = permit.get("duration_id")
        try:
            duration_id = int(duration_id) if duration_id is not None else None
        except Exception:
            duration_id = None

        if not duration_id:
            return

        shifts_sorted = sorted(shifts_for_day, key=lambda x: x[0])

        covered = set(self._permit_covered_shift_indexes(shifts_sorted, duration_id))

        original_expected = len(shifts_sorted) * 2

        covered_marks = len(covered) * 2
        new_expected = max(0, original_expected - covered_marks)

        day["permit_duration_id"] = duration_id
        day["permit_expected_reduction"] = covered_marks

        day["expected_marks"] = new_expected

        remaining_starts = [s for idx, (s, _) in enumerate(shifts_sorted) if idx not in covered]
        day["expected_start"] = self._minutes_to_hhmm(min(remaining_starts)) if remaining_starts else None


    @handle_exceptions
    def salary_calculate_stats(self, period_id, editor_user_id):
        """Calcula stats para todos los usuarios de un periodo y los guarda.
        Replica exactamente la lógica de buildMonthStats del frontend."""
        period, pc = self.salary_repository.get_period_by_id(period_id)
        if pc != 200 or not period:
            return "Periodo no encontrado", 404

        users, uc = self.user_repository.get_all_active_users()
        if uc != 200:
            return users, uc

        calculated = 0
        now = peru_time()
        today_iso = now.date().isoformat()

        # Calcular el offset a partir del period_id
        today_date = now.date()
        from calendar import monthrange
        base_month = date(today_date.year, today_date.month, 1)
        mid_date = period.start_date + (period.end_date - period.start_date) // 2
        period_month = mid_date.replace(day=1)

        # Diferencia en meses
        offset = (period_month.year - base_month.year) * 12 + (period_month.month - base_month.month)

        

        for user in users:
            if user.level_id in [1, 5]:
                continue
            if user.department_id == 7:
                continue
            if user.id == 23:
                continue

            try:
                # Reusar summary_by_offset que ya construye el grid completo
                data = {"offset": offset, "user_id": user.id}
                result, rc = self.summary_by_offset(data)
                if rc != 200:
                    continue

                weeks = result.get("weeks", [])
                if not weeks:
                    continue

                target = 0
                worked = 0
                tolerance_accum = 0
                tardies = 0
                incompletes = 0

                # Art. 23: Contar días de vacaciones directamente de la BD
                # para incluir sábados, domingos y feriados dentro del rango
                vacations, _ = self.attendance_repository.count_vacation_days_in_period(
                    user.id, period.start_date, period.end_date
                )

                for w in weeks:
                    for day in w.get("days", []):
                        if not day.get("in_period"):
                            continue
                        if day.get("is_summary"):
                            continue

                        # Target: todo el periodo (incluye futuro)
                        target += int(day.get("target_min") or 0)

                        # Worked, tardanzas: solo hasta hoy
                        day_date = day.get("date", "")
                        if not day_date or day_date > today_iso:
                            continue

                        worked += int(day.get("worked_min") or 0)

                        if day.get("incomplete"):
                            incompletes += 1

                        # Replicar isLateDay del frontend
                        if self._is_late_day(day):
                            late_min = self._late_minutes(day)
                            if late_min > 0:
                                tardies += 1
                                tolerance_accum += late_min

                # Fórmula idéntica al frontend
                tolerance_planned = round(target * 0.01)
                base_excess = max(0, tolerance_accum - tolerance_planned)
                calc_excess = round(base_excess * 1.5)
                calc_obj = target + calc_excess
                compliance = (worked * 100 / calc_obj) if calc_obj > 0 else 0

                stats_data = {
                    "user_id": user.id,
                    "period_id": period_id,
                    "target_min": target,
                    "worked_min": worked,
                    "tolerance_planned_min": tolerance_planned,
                    "tolerance_accum_min": tolerance_accum,
                    "base_excess_min": base_excess,
                    "calc_excess_min": calc_excess,
                    "calc_obj_min": calc_obj,
                    "tardiness_count": tardies,
                    "vacation_days": vacations,
                    "incomplete_days": incompletes,
                    "compliance_pct": math.floor(compliance * 100) / 100,
                    "calculated_at": now,
                    "calculated_by": editor_user_id,
                }

                logging.info(f"=== SALARY STATS para user {user.id} ===")
                logging.info(f"offset: {offset}, period: {period.name}")
                logging.info(f"result weeks: {len(result.get('weeks', []))}")
                logging.info(f"target: {target}, worked: {worked}, tardies: {tardies}")
                logging.info(f"compliance: {compliance}")

                self.salary_repository.upsert_period_stats(stats_data)
                calculated += 1

            except Exception as ex:
                logging.warning(f"Error calculando stats para user {user.id}: {ex}")
                continue

        # Calcular saldos de vacaciones automáticamente
        try:
            self.calculate_leave_balances(period_id)
        except Exception as ex:
            logging.warning(f"Error calculando leave balances: {ex}")

        return {"calculated": calculated, "period_id": period_id}, 200


    def _is_late_day(self, day):
        """Replica isLateDay() del frontend"""
        if not day.get("in_period"):
            return False
        if day.get("is_summary"):
            return False
        if day.get("is_holiday"):
            return False
        if day.get("is_vacation"):
            return False

        # Permiso sin expected_start = no cuenta tardanza
        if day.get("is_permit") and not day.get("expected_start"):
            return False

        # Permiso con duration_id 1 (todo el día) o 3 (mañana) = no cuenta
        permit = day.get("permit") or {}
        duration_id = permit.get("duration_id") or day.get("permit_duration_id")
        if day.get("is_permit") and duration_id in [1, 3]:
            return False

        intervals = day.get("intervals") or []
        if not intervals:
            return False

        first = intervals[0]
        start = (first.get("start") or "").strip()
        expected = (day.get("expected_start") or "").strip()

        if not start or not expected:
            return False

        return self._late_minutes(day) > 0


    def _late_minutes(self, day):
        """Replica lateMinutes() del frontend"""
        intervals = day.get("intervals") or []
        if not intervals:
            return 0

        first = intervals[0]
        start = (first.get("start") or "").strip()
        expected = (day.get("expected_start") or "").strip()

        if not start or not expected:
            return 0

        s = self._hhmm_to_minutes(start)
        e = self._hhmm_to_minutes(expected)

        return max(0, s - e)

        
    @handle_exceptions
    def salary_calculate(self, period_id, editor_user_id):
        """Calcula salary para todos los usuarios con stats en el periodo.
        Solo recalcula los que están en draft."""
        period, pc = self.salary_repository.get_period_by_id(period_id)
        if pc != 200 or not period:
            return "Periodo no encontrado", 404

        stats_list, sc = self.salary_repository.get_all_stats_by_period(period_id)
        if sc != 200:
            return stats_list, sc

        calculated = 0
        skipped = 0

        for stats in stats_list:
            config, cc = self.salary_repository.get_salary_config(stats.user_id, period.end_date)
            if cc != 200 or not config:
                continue

            base = float(config.base_salary)
            compliance = float(stats.compliance_pct or 0)
            compliance = math.floor(compliance * 100) / 100
            factor = min(compliance / 100, 1.0)
            factor = math.floor(factor * 10000) / 10000 
            final = math.floor(base * factor * 100) / 100

            salary_data = {
                "user_id": stats.user_id,
                "period_id": period_id,
                "stats_id": stats.id,
                "business_id": config.business_id,
                "base_salary": base,
                "compliance_pct": compliance,
                "factor": round(factor, 4),
                "final_salary": final,
            }

            result, rc = self.salary_repository.upsert_salary_period_if_draft(salary_data)
            if result == "skipped":
                skipped += 1
            else:
                calculated += 1

        return {
            "calculated": calculated,
            "skipped": skipped,
            "period_id": period_id,
        }, 200


    @handle_exceptions
    def salary_recalculate_single(self, salary_id, editor_user_id):
        """Recalcula un salary específico, reseteando a draft"""
        salary, sc = self.salary_repository.get_salary_by_id(salary_id)
        if sc != 200 or not salary:
            return "Salario no encontrado", 404

        # Recalcular stats para este usuario
        period, pc = self.salary_repository.get_period_by_id(salary.period_id)
        if pc != 200 or not period:
            return "Periodo no encontrado", 404

        # Obtener config vigente
        config, cc = self.salary_repository.get_salary_config(salary.user_id, period.end_date)
        if cc != 200 or not config:
            return "Sin configuración de salario", 404

        # Obtener stats
        stats, stc = self.salary_repository.get_period_stats(salary.user_id, salary.period_id)
        if stc != 200 or not stats:
            return "Sin stats calculados", 404

        base = float(config.base_salary)
        compliance = float(stats.compliance_pct or 0)
        compliance = math.floor(compliance * 100) / 100
        factor = min(compliance / 100, 1.0)
        factor = math.floor(factor * 10000) / 10000
        final = math.floor(base * factor * 100) / 100

        update_data = {
            "stats_id": stats.id,
            "business_id": config.business_id,
            "base_salary": base,
            "compliance_pct": compliance,
            "factor": round(factor, 4),
            "final_salary": final,
        }

        return self.salary_repository.reset_and_update_salary(salary_id, update_data)


    @handle_exceptions
    def salary_get_period(self, period_id):
        """Obtiene salarios del periodo para mostrar en la tabla"""
        salaries, sc = self.salary_repository.get_salaries_by_period(period_id)
        if sc != 200:
            return salaries, sc

        result = []
        for s in salaries:
            result.append({
                "id": s.id,
                "user_id": s.user_id,
                "user_name": format_name(s.user.name) if s.user else "-",
                "user_image": s.user.image if s.user else "user_default.jpg",
                "department_name": s.user.department.name if s.user and s.user.department else "-",
                "business_name": s.business.name if s.business else "-",
                "base_salary": float(s.base_salary),
                "compliance_pct": float(s.compliance_pct),
                "factor": float(s.factor),
                "adjustment": float(s.adjustment or 0),
                "final_salary": float(s.final_salary),
                "status": s.status,
            })

        return result, 200


    @handle_exceptions
    def salary_get_user(self, data):
        """Obtiene salary de un usuario específico para el card del frontend"""

        user_id = data.get("user_id")
        period_id = data.get("period_id")

        salary, sc = self.salary_repository.get_salary_period(user_id, period_id)
        if sc != 200:
            return salary, sc

        if not salary:
            return None, 200

        return {
            "base_salary": float(salary.base_salary),
            "compliance_pct": float(salary.compliance_pct),
            "factor": float(salary.factor),
            "adjustment": float(salary.adjustment or 0),
            "final_salary": float(salary.final_salary),
            "business_name": salary.business.name if salary.business else "-",
            "status": salary.status,
        }, 200


    @handle_exceptions
    def salary_config_save(self, data):
        """Guardar/actualizar sueldo base de un usuario"""
        user_id = data.get("user_id")
        base_salary = data.get("base_salary")
        business_id = data.get("business_id")
        effective_from = data.get("effective_from")

        if not user_id or not base_salary or not business_id or not effective_from:
            return "Datos incompletos", 400

        from application.utils import parse_date_iso
        config_data = {
            "user_id": int(user_id),
            "business_id": int(business_id),
            "base_salary": float(base_salary),
            "effective_from": parse_date_iso(effective_from),
        }

        result, rc = self.salary_repository.upsert_salary_config(config_data)
        return "Configuración guardada", rc


    @handle_exceptions
    def salary_config_get(self, user_id):
        """Obtiene la config de salary vigente de un usuario"""
        config, cc = self.salary_repository.get_salary_config_by_user(user_id)
        if cc != 200:
            return config, cc

        if not config:
            return None, 200

        return {
            "user_id": config.user_id,
            "business_id": config.business_id,
            "business_name": config.business.name if config.business else "-",
            "base_salary": float(config.base_salary),
            "currency": config.currency,
            "effective_from": config.effective_from.isoformat(),
            "effective_to": config.effective_to.isoformat() if config.effective_to else None,
        }, 200


    @handle_exceptions
    def bank_account_get(self, user_id):
        return self.salary_repository.get_bank_accounts_by_user(int(user_id))

    @handle_exceptions
    def bank_account_save(self, data):
        user_id = data.get("user_id")
        business_id = data.get("business_id")
        account_number = (data.get("account_number") or "").strip()
        account_type = data.get("account_type", "A")
        doc_type = data.get("doc_type", "1")
        currency = data.get("currency", "S")

        if not user_id or not business_id or not account_number:
            return "Datos incompletos", 400

        return self.salary_repository.upsert_bank_account(int(user_id), {
            "business_id":    int(business_id),
            "account_type":   account_type,
            "account_number": account_number,
            "doc_type":       doc_type,
            "currency":       currency,
        })

    @handle_exceptions
    def salary_approve_rrhh(self, salary_id, approved_by):
        return self.salary_repository.approve_rrhh(salary_id, approved_by)


    @handle_exceptions
    def salary_approve_mgr(self, salary_id, approved_by):
        return self.salary_repository.approve_mgr(salary_id, approved_by)


    @handle_exceptions
    def salary_set_adjustment(self, salary_id, adjustment, adjusted_by):
        if adjustment is None:
            return "Ajuste requerido", 400
        return self.salary_repository.set_adjustment(salary_id, adjustment, adjusted_by)


    @handle_exceptions
    def salary_approve(self, salary_id, approved_by):
        """Legacy"""
        return self.salary_repository.approve_salary(salary_id, approved_by)


    @handle_exceptions
    def salary_generate_telecredito(self, period_id, business_id):
        """Genera el archivo TXT de Telecrédito BCP para pago de haberes"""

        # Config bancaria de la empresa
        bank_config, bc = self.salary_repository.get_business_bank_config(business_id)
        if bc != 200 or not bank_config:
            return "Configuración bancaria no encontrada para esta empresa", 404

        # Periodo
        period, pc = self.salary_repository.get_period_by_id(period_id)
        if pc != 200 or not period:
            return "Periodo no encontrado", 404

        # Salarios aprobados de esta empresa
        salaries, sc = self.salary_repository.get_approved_salaries_by_period_and_business(period_id, business_id)
        if sc != 200:
            return salaries, sc

        if not salaries:
            return "No hay salarios aprobados para generar", 422

        # Construir líneas de detalle
        detail_lines = []
        total_amount  = 0
        total_control = 0

        # TotalControl campo: sum of significant digits from cargo account
        cargo_acct_num = bank_config.account_number.strip()
        if len(cargo_acct_num) > 3:
            try:
                total_control += int(cargo_acct_num[3:])
            except ValueError:
                pass

        for salary in salaries:
            user = salary.user
            if not user:
                continue

            # Cuenta bancaria del trabajador
            bank_acct, bac = self.salary_repository.get_bank_account(user.id, business_id)
            if bac != 200 or not bank_acct:
                continue

            amount = float(salary.final_salary)
            total_amount += amount
            doc  = (user.document or "").strip()
            name = (user.name or "").strip()

            # TotalControl: add significant digits of this abono account
            abono_acct_num = bank_acct.account_number.strip()
            try:
                # type B (20-char inter-bank): chars 11+; others (C/M 13-char): chars 4+
                offset = 10 if bank_acct.account_type == "B" else 3
                if len(abono_acct_num) > offset:
                    total_control += int(abono_acct_num[offset:])
            except ValueError:
                pass

            # doc padded to 12 for DNI (type "1") or other types (campo5 = 12 chars)
            doc_padded = (doc.ljust(8)[:8] + "    ") if bank_acct.doc_type == "1" else doc.ljust(12)[:12]

            # Detail line (195 chars) — field layout per BCP Telecrédito spec
            line = (
                "2"                                                      # [0]     tipo registro
                + bank_acct.account_type                                 # [1]     tipo cuenta abono
                + bank_acct.account_number.ljust(20)[:20]                # [2:22]  nro cuenta abono (20)
                + bank_acct.doc_type                                     # [22]    tipo doc empleado
                + doc_padded                                             # [23:35] nro doc (12)
                + "   "                                                  # [35:38] correlativo doc (3)
                + name.ljust(75)[:75]                                    # [38:113] nombre (75)
                + f"Referencia Beneficiario {doc_padded}".ljust(40)[:40] # [113:153] ref beneficiario (40)
                + f"Ref Emp {doc_padded}".ljust(20)[:20]                 # [153:173] ref empresa (20)
                + ("0001" if bank_acct.currency == "S" else "1001")      # [173:177] moneda abono (4)
                + f"{amount:017.2f}"                                     # [177:194] importe (17)
                + "S"                                                    # [194]   flag validar IDC
            )

            detail_lines.append(line)

        # Fecha de proceso = último día del periodo
        fecha = period.end_date.strftime("%Y%m%d")
        count = len(detail_lines)

        # Moneda de cuenta cargo: derivada del 11º dígito (índice 10) del nro de cuenta
        # "0" → soles "0001", "1" → dólares "1001"
        moneda_char  = cargo_acct_num[10] if len(cargo_acct_num) > 10 else "0"
        moneda_cargo = "0001" if moneda_char == "0" else "1001"

        # Header line (113 chars) — field layout per BCP Telecrédito spec
        header = (
            "1"                                          # [0]     tipo registro
            + f"{count:06d}"                             # [1:7]   cantidad abonos (6)
            + fecha                                      # [7:15]  fecha proceso (8)
            + "X"                                         # [15]    subtipo planilla: X = haberes
            + bank_config.account_type                   # [16]    tipo cuenta cargo (1)
            + moneda_cargo                               # [17:21] moneda cuenta cargo (4)
            + cargo_acct_num.ljust(20)[:20]              # [21:41] nro cuenta cargo (20)
            + f"{total_amount:017.2f}"                   # [41:58] monto total planilla (17)
            + bank_config.reference.ljust(40)[:40]       # [58:98] referencia planilla (40)
            + f"{total_control:015d}"                    # [98:113] total control (15)
        )

        # Generar contenido
        content = header + "\n" + "\n".join(detail_lines)

        return {
            "content": content,
            "filename": f"telecredito_{salary.business.name}_{period.name.replace(' ', '_')}.txt",
            "count": count,
            "total": total_amount,
        }, 200

    @handle_exceptions
    def salary_generate_bbva_cash(self, period_id, business_id):
        """Genera el archivo TXT BBVA Cash para pago de haberes (formato centavos)"""
        bank_config, bc = self.salary_repository.get_business_bank_config(business_id)
        if bc != 200 or not bank_config:
            return "Configuración bancaria no encontrada para esta empresa", 404

        period, pc = self.salary_repository.get_period_by_id(period_id)
        if pc != 200 or not period:
            return "Periodo no encontrado", 404

        salaries, sc = self.salary_repository.get_approved_salaries_by_period_and_business(period_id, business_id)
        if sc != 200:
            return salaries, sc
        if not salaries:
            return "No hay salarios aprobados para generar", 422

        fecha = period.end_date.strftime("%Y%m%d")
        detail_lines = []
        total_centavos = 0

        for salary in salaries:
            user = salary.user
            if not user:
                continue
            bank_acct, bac = self.salary_repository.get_bank_account(user.id, business_id)
            if bac != 200 or not bank_acct:
                continue

            centavos = int(round(float(salary.final_salary) * 100))
            total_centavos += centavos

            doc      = (user.document or "").strip()
            cuenta   = bank_acct.account_number.ljust(20)[:20]
            line = (
                "0680"                      # [0:4]   tipo registro
                + doc.ljust(15)[:15]        # [4:19]  referencia (DNI)
                + "001"                     # [19:22] servicio: soles haberes
                + cuenta                   # [22:42] cuenta abono
                + f"{centavos:014d}"        # [42:56] importe centavos
                + fecha                    # [56:64] fecha YYYYMMDD
                + " " * 36                 # [64:100] padding
            )
            detail_lines.append(line)

        emisora  = bank_config.company_code.strip().zfill(5)[-5:]
        count    = len(detail_lines)
        header = (
            "038010011"                     # [0:9]   magic BBVA Cash
            + emisora                       # [9:14]  código emisora
            + f"{count:07d}"               # [14:21] cantidad registros PEN
            + f"{total_centavos:015d}"     # [21:36] total PEN centavos
            + "0000000"                    # [36:43] registros USD
            + "000000000000000"            # [43:58] total USD
            + fecha                        # [58:66] fecha YYYYMMDD
            + " " * 34                     # [66:100] padding
        )

        content = header + "\r\n" + "\r\n".join(detail_lines) + "\r\n"
        biz_name = salaries[0].business.name if salaries else str(business_id)

        return {
            "content": content,
            "filename": f"bbva_haberes_{biz_name}_{period.name.replace(' ', '_')}.txt",
            "count": count,
            "total": round(total_centavos / 100, 2),
        }, 200

    # ── Leave Balance ──────────────────────────────────────────────────

    @handle_exceptions
    def calculate_leave_balances(self, period_id):
        """Calcula el saldo de vacaciones para todos los usuarios del periodo.
        Se llama automáticamente después de salary_calculate_stats."""
        stats_list, sc = self.salary_repository.get_all_stats_by_period(period_id)
        if sc != 200:
            return stats_list, sc

        calculated = 0
        for stats in stats_list:
            # Obtener balance del periodo anterior
            prev_bal, pc = self.attendance_repository.get_leave_balance_prev(stats.user_id, period_id)
            prev_balance = float(prev_bal.balance) if prev_bal else 0

            data = {
                "user_id": stats.user_id,
                "period_id": period_id,
                "vacation_used": stats.vacation_days or 0,
                "prev_balance": prev_balance,
            }
            self.attendance_repository.upsert_leave_balance(data)
            calculated += 1

        return {"calculated": calculated}, 200


    @handle_exceptions
    def get_leave_balance_for_user(self, user_id, period_id):
        """Obtiene el saldo de vacaciones de un usuario en un periodo"""
        bal, bc = self.attendance_repository.get_leave_balance(user_id, period_id)
        if bc != 200:
            return bal, bc

        if not bal:
            return {
                "vacation_used": 0,
                "prev_balance": 0,
                "manual_adj": 0,
                "balance": 0,
                "adjusted_by": None,
                "adjusted_at": None,
            }, 200

        return {
            "vacation_used": int(bal.vacation_used),
            "prev_balance": float(bal.prev_balance),
            "manual_adj": float(bal.manual_adj),
            "balance": float(bal.balance),
            "adjusted_by": bal.adjusted_by,
            "adjusted_at": bal.adjusted_at.isoformat() if bal.adjusted_at else None,
        }, 200


    @handle_exceptions
    def set_leave_manual_adj(self, user_id, period_id, manual_adj, adjusted_by):
        if manual_adj is None:
            return "Ajuste requerido", 400
        if not period_id:
            return "Periodo requerido", 400

        result, rc = self.attendance_repository.set_leave_manual_adj(
            int(user_id), int(period_id), float(manual_adj), int(adjusted_by)
        )
        if rc != 200:
            return result, rc

        return "Ajuste aplicado", 200


    # ── Medical Leave (Descanso Médico) ───────────────────────────────

    @handle_exceptions
    def medical_leave_request(self, req):
        """Crea una solicitud de Descanso Médico con archivos adjuntos.
        Recibe un request de Flask con files + form data (multipart)."""
        from flask import request as flask_request

        form = req.form
        files = req.files.getlist("attachments[]")

        user_id_creator = int(get_jwt_identity())
        target_user_id = int(form.get("user_id") or user_id_creator)

        # Validaciones básicas
        if not form.get("start_date"):
            return "Fecha de inicio requerida", 422

        if not files or not any(f and f.filename for f in files):
            return "Debes adjuntar al menos un archivo", 422

        # Validar extensiones
        for f in files:
            if not f or not f.filename:
                continue
            if not allowed_extension(f.filename):
                return f"Tipo de archivo no permitido: {f.filename}", 422

        # Determinar status inicial según permisos del creador
        if self._has_perm(user_id_creator, 'approve_leave_manager'):
            initial_status = 4
        elif self._has_perm(user_id_creator, 'approve_leave_rrhh'):
            initial_status = 3
        elif self._has_perm(user_id_creator, 'approve_leave'):
            initial_status = 2
        else:
            initial_status = 1

        start_date = parse_date_iso(form.get("start_date"))
        end_date_str = form.get("end_date")
        end_date = parse_date_iso(end_date_str) if end_date_str else start_date

        if end_date < start_date:
            return "La fecha fin no puede ser menor a la fecha inicio", 422

        # Crear solicitud
        leave_data = {
            "user_id": target_user_id,
            "type": "medical",   # Flag especial
            "_initial_status": initial_status,
            "start_date": start_date,
            "end_date": end_date,
            "description": form.get("description", ""),
        }

        # Insertar con request_type especial
        from application.db_models.leave_model import LeaveRequest
        from flask import g

        obj = LeaveRequest(
            user_id=target_user_id,
            request_type="Descanso Médico",
            status_id=initial_status,
            start_date=start_date,
            end_date=end_date,
            description=form.get("description", ""),
            created_at=peru_time(),
        )
        g.db_session.add(obj)
        g.db_session.commit()
        leave_id = obj.id

        # Guardar archivos
        saved_files = []
        try:
            upload_dir = upload_path(Paths.LEAVES)
            for f in files:
                if not f or not f.filename:
                    continue
                original = f.filename
                ext = file_extension(original)
                safe = secure_filename(original) or f"file.{ext}"
                stored = f"{uuid.uuid4().hex}_{safe}"
                full_path = os.path.join(upload_dir, stored)
                f.save(full_path)

                size_bytes = os.path.getsize(full_path)
                mime = getattr(f, "mimetype", None)

                self.attendance_repository.add_leave_attachment({
                    "leave_request_id": leave_id,
                    "original_name": original,
                    "stored_name": stored,
                    "mime_type": mime,
                    "size_bytes": size_bytes,
                    "uploaded_by": user_id_creator,
                })
                saved_files.append(stored)
        except Exception as ex:
            logging.exception(f"Error guardando archivos: {ex}")
            # Cleanup archivos ya guardados
            for s in saved_files:
                try:
                    os.remove(os.path.join(Paths.LEAVES, s))
                except Exception:
                    pass
            return f"Error guardando archivos: {ex}", 500

        # Si el creador tiene permiso de aprobación total, generar adjustments directo
        if initial_status == 4:
            try:
                self._create_adjustments_for_medical_leave(obj)
            except Exception as ex:
                logging.exception(f"Error creando adjustments para LI-{leave_id}: {ex}")

        socketio.emit("attendance_update_leaves", {})
        return {"id": leave_id, "attachments": len(saved_files)}, 200


    def _create_adjustments_for_medical_leave(self, leave):
        """Genera attendance_day_adjustment por cada shift del profile del usuario,
        para cada día en el rango [start_date, end_date] del descanso médico.
        Un adjustment por shift = respeta la hora de refrigerio (no se regala)."""
        from datetime import timedelta

        user_id = leave.user_id
        desc_tag = f"Descanso Médico - LI-{leave.id}"

        # Eliminar adjustments previos del mismo leave (por si se reaprueba)
        self.attendance_repository.delete_day_adjustments_by_description(desc_tag)

        d = leave.start_date
        end = leave.end_date or leave.start_date

        created = 0
        while d <= end:
            # Obtener profile vigente para ese día
            profile, pc = self.attendance_repository.get_profile_for_user_on_date(user_id, d)
            if pc != 200 or not profile:
                d += timedelta(days=1)
                continue

            shifts, src = self.attendance_repository.get_shifts_for_profile(profile.id)
            if src != 200:
                d += timedelta(days=1)
                continue

            wd = d.weekday()
            day_shifts = [s for s in shifts if s.weekday == wd]

            for shift in day_shifts:
                self.attendance_repository.add_day_adjustment({
                    "date": d,
                    "start_time": shift.start_time,
                    "end_time": shift.end_time,
                    "scope": "user",
                    "user_id": user_id,
                    "profile_id": profile.id,
                    "description": desc_tag,
                })
                created += 1

            d += timedelta(days=1)

        logging.info(f"Creados {created} adjustments para LI-{leave.id}")
        return created


    @handle_exceptions
    def add_leave_attachments(self, request):
        leave_id = request.view_args.get("leave_id")
        user_id = int(get_jwt_identity())
        files = request.files.getlist("attachments[]")
        if not files:
            return "No files provided", 400

        upload_dir = Paths.LEAVES
        saved = []
        try:
            for f in files:
                if not f or not f.filename:
                    continue
                original = f.filename
                ext = file_extension(original)
                safe = secure_filename(original) or f"file.{ext}"
                stored = f"{uuid.uuid4().hex}_{safe}"
                full_path = os.path.join(upload_dir, stored)
                f.save(full_path)
                size_bytes = os.path.getsize(full_path)
                mime = getattr(f, "mimetype", None)
                self.attendance_repository.add_leave_attachment({
                    "leave_request_id": leave_id,
                    "original_name": original,
                    "stored_name": stored,
                    "mime_type": mime,
                    "size_bytes": size_bytes,
                    "uploaded_by": user_id,
                })
                saved.append(stored)
        except Exception as ex:
            for s in saved:
                try:
                    os.remove(os.path.join(upload_dir, s))
                except Exception:
                    pass
            return f"Error guardando archivos: {ex}", 500

        return {"added": len(saved)}, 200

    @handle_exceptions
    def get_leave_attachments(self, leave_id):
        rows, rc = self.attendance_repository.get_leave_attachments(leave_id)
        if rc != 200:
            return rows, rc

        def _ext(name):
            return name.rsplit(".", 1)[-1].lower() if "." in (name or "") else ""

        result = [{
            "id": a.id,
            "original_name": a.original_name,
            "ext": _ext(a.original_name),
            "mime_type": a.mime_type,
            "size_bytes": int(a.size_bytes or 0),
            "uploaded_at": a.uploaded_at.isoformat() if a.uploaded_at else None,
            "uploader_name": format_name(a.uploader.name) if a.uploader else "-",
            "inline_url": f"/attendance/leave/attachment/{a.id}?disposition=inline",
            "download_url": f"/attendance/leave/attachment/{a.id}?disposition=attachment",
            "preview_url": f"/attendance/leave/attachment/{a.id}/preview",
        } for a in rows]

        return result, 200


    def attachment_stream(self, attachment_id, disposition="inline"):
        from flask import send_file, abort
        row, rc = self.attendance_repository.get_leave_attachment_by_id(attachment_id)
        if rc != 200 or not row:
            abort(404)
        full_path = os.path.join(Paths.LEAVES, row.stored_name)
        if not os.path.isfile(full_path):
            abort(404)
        return send_file(
            full_path,
            mimetype=row.mime_type or "application/octet-stream",
            as_attachment=(disposition == "attachment"),
            download_name=row.original_name,
        )

    @handle_exceptions
    def attachment_preview(self, attachment_id):
        row, rc = self.attendance_repository.get_leave_attachment_by_id(attachment_id)
        if rc != 200 or not row:
            return "Not found", 404
        ext = row.original_name.rsplit(".", 1)[-1].lower() if "." in (row.original_name or "") else ""
        inline_url = f"/attendance/leave/attachment/{row.id}?disposition=inline"
        if ext in {"png", "jpg", "jpeg", "webp", "gif", "pdf"}:
            return {"kind": "url", "url": inline_url, "name": row.original_name}, 200
        full_path = os.path.join(Paths.LEAVES, row.stored_name)
        if not os.path.isfile(full_path):
            return "File missing", 404
        if ext in {"txt", "xml"}:
            with open(full_path, "r", encoding="utf-8", errors="replace") as fp:
                text = fp.read(200_000)
            return {"kind": "text", "text": text, "name": row.original_name}, 200
        return {
            "kind": "download",
            "name": row.original_name,
            "message": "Vista previa no disponible",
            "download_url": f"/attendance/leave/attachment/{row.id}?disposition=attachment",
        }, 200

    @handle_exceptions
    def delete_leave_attachment(self, attachment_id):
        row, rc = self.attendance_repository.get_leave_attachment_by_id(attachment_id)
        if rc != 200 or not row:
            return "Not found", 404
        full_path = os.path.join(Paths.LEAVES, row.stored_name)
        _, drc = self.attendance_repository.delete_leave_attachment(attachment_id)
        if drc != 200:
            return "Error al eliminar", 500
        try:
            if os.path.isfile(full_path):
                os.remove(full_path)
        except OSError:
            pass
        return {"deleted": attachment_id}, 200

    def get_leave_attachment_file(self, attachment_id, disposition="inline"):
        from flask import abort
        return self.attachment_stream(attachment_id, disposition=disposition)