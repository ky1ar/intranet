import logging, os, re
import pandas as pd
from io import BytesIO
from datetime import datetime, timedelta, date
from application.handlers import handle_exceptions
from application.utils import parse_date_iso, parse_time, format_name, format_datetime, format_date
from application.services.push_service import PushSender
from application.repository.attendance_repository import AttendanceRepository
from application.repository.user_repository import UserRepository
from application import socketio
from flask_jwt_extended import get_jwt_identity


_RE_DATE_RANGE = re.compile(r"(\d{4}-\d{2}-\d{2})\s*~\s*(\d{4}-\d{2}-\d{2})")
_RE_TIME = re.compile(r"\d{2}:\d{2}")
_RE_DNI = re.compile(r"\d{8}")


class AttendanceService:
    def __init__(self):
        self.attendance_repository = AttendanceRepository()
        self.user_repository = UserRepository()
        self.push_service = PushSender()
        self.management_dep = 7
        self.worker_lvl = 2
        self.leader_lvl = 3
        self.admin_lvl = 4


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
        
        level_id = user.level_id
        department_id = user.department_id

        if department_id == self.management_dep or user_id == 23:
            return self._get_manager_request_list(user_id)
        
        if level_id == self.leader_lvl:
            return self._get_leader_request_list(user_id, department_id)
        
        return self._get_worker_request_list(user_id)
    

    @handle_exceptions
    def _get_worker_request_list(self, user_id):
        leave_requests, lrc = self.attendance_repository.get_leave_requests([user_id])
        if lrc != 200:
            return leave_requests, lrc
        
        return self._format_requests_reponse(leave_requests, user_id, self.worker_lvl)


    @handle_exceptions
    def _get_leader_request_list(self, user_id, department_id):
        department_user_ids, duic = self.user_repository.get_user_ids_by_department(department_id)
        if duic != 200:
            return department_user_ids, duic
    
        leave_requests, lrc = self.attendance_repository.get_leave_requests(department_user_ids)
        if lrc != 200:
            return leave_requests, lrc
        
        return self._format_requests_reponse(leave_requests, user_id, self.leader_lvl)
    

    @handle_exceptions
    def _get_manager_request_list(self, user_id):
        leave_requests, lrc = self.attendance_repository.get_leave_requests([])
        if lrc != 200:
            return leave_requests, lrc
        
        return self._format_requests_reponse(leave_requests, user_id, self.leader_lvl)
    

    @handle_exceptions
    def _format_requests_reponse(self, leave_requests, user_id, level):
        return {
            "requests": [
                {
                    "id": leave.id,
                    "requester_name": format_name(leave.user.name) if user_id != leave.user_id else 'Tú',
                    "requester_image": leave.user.image,
                    "request_type": leave.request_type,
                    "status_name": leave.status.name,
                    "status_slug": leave.status.slug,
                } for leave in leave_requests
            ],
            "viewer_level_id": level,
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

        items = []
        for a in best:
            s = self._minutes_to_hhmm(self._time_to_minutes(a.start_time))
            e = self._minutes_to_hhmm(self._time_to_minutes(a.end_time))
            label = (a.description or "").strip() or "Ajuste"
            items.append({
                "label": label,
                "value": f"{s} - {e}",
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
            payload["available_leave"] = int(leave_adjustment.available)
            payload["finish_date"] = leave_adjustment.finish_date
            
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
                    day["expected_marks"] = 0
                    day["expected_start"] = None
                    day["target_min"] = 0
                    day["worked_min"] = 0
                    day["delta_min"] = 0
                    day["incomplete"] = False
                    day["incomplete_count"] = 0
                    day["has_adjustment"] = False
                    day["adjustment_bonus_min"] = 0
                    day["adjustment_marks"] = 0
                    day["adjustment_items"] = []
                    day["not_started_yet"] = True
                    day["is_summary"] = False
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
        
        data["level_id"] = user.level_id

        start_date = parse_date_iso(data.get("start_date"))
        data["start_date"] = start_date

        end_date = data.get("end_date")
        data["end_date"] = parse_date_iso(end_date) if end_date else start_date

        res, rc = self.attendance_repository.insert_leave_request(data)
        if rc != 200:
            return res, rc
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
        
        level_id = user.level_id
        department_id = user.department_id

        if department_id == self.management_dep:
            modal = {
                1: "approve",
                2: "approve",
            }
            return self._format_get_request(modal, user, leave)
        
        elif level_id in [self.leader_lvl, self.admin_lvl]:
            
            modal = {
                1: "approve",
                2: "edit" if leave.user_id == user_id else 'view',
            }
            return self._format_get_request(modal, user, leave)
        modal = {
            1: "edit",
        }
        return self._format_get_request(modal, user, leave)


    @handle_exceptions
    def _format_get_request(self, modal, user, leave):
        status_id = leave.status_id
        dto = {
            "id": leave.id,
            "modal": modal.get(status_id, "view"),
            "type": 'permit' if leave.request_type == 'Permiso' else 'vacation',
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
            "self_created": True if user.id == leave.user_id else False,
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
        
        if data.get("delete") is True:
            delete, dc = self.attendance_repository.soft_delete(leave_id)
            if dc != 200:
                return delete, dc

        elif action == "approve":
            level_id = user.level_id
            department_id = user.department_id
            user_name = user.name

            status_id = None
            if department_id == self.management_dep:
                status_id = 3
            elif level_id in [self.leader_lvl, self.admin_lvl]:
                status_id = 2
            else:
                return "No autorizado para aprobar", 403

            status, sc = self.attendance_repository.set_status(leave_id, status_id)
            if sc != 200:
                return status, sc
            
            leave, lc = self.attendance_repository.get_leave_by_id(leave_id)
            if lc != 200:
                return leave, lc

            creator_id = leave.user_id
            creator_name = leave.user.name
            creator_department_id = leave.user.department_id
            creator_level_id = leave.user.level_id
            is_permit = leave.request_type == 'Permiso'

            if department_id == self.management_dep:
                self.push_service.send_to_user(
                    user_id=creator_id,
                    title="Permiso aprobado" if is_permit else "Vacaciones aprobadas",
                    body=f"Tu solicitud de licencia LI-{leave_id} ha sido aprobada por Gerencia.",
                )

                if creator_level_id != self.leader_lvl:
                    leader, lc = self.user_repository.get_leader(creator_department_id)
                    if lc != 200:
                        return leader, lc
                    
                    self.push_service.send_to_user(
                        user_id=leader.id,
                        title="La soclicitud se aprobó",
                        body=f"Gerencia acaba de aprobar la solicitud de licencia de {format_name(creator_name, True)}.",
                    )
            
            elif level_id in [self.leader_lvl, self.admin_lvl]:
                # Avisar creador
                self.push_service.send_to_user(
                    user_id=creator_id,
                    title="Solicitud validada",
                    body=f"{format_name(user_name, True)} aprobó tu solicitud de licencia LI-{leave_id}. En espera de Gerencia.",
                )

                manager, lc = self.user_repository.get_manager()
                if lc != 200:
                    return manager, lc
                
                # Avisar manager
                self.push_service.send_to_user(
                    user_id=manager.id,
                    title="Licencia pendiente de aprobación",
                    body=f"La solicitud de licencia de {format_name(creator_name, True)} necesita tu aprobación.",
                )

        elif action == "reject":
            result, code = self.attendance_repository.set_status(leave_id, status_id=4)
            if code != 200:
                return result, code

            level_id = user.level_id
            department_id = user.department_id
            user_name = user.name

            leave, lc = self.attendance_repository.get_leave_by_id(leave_id)
            if lc != 200:
                return leave, lc

            creator_id = leave.user_id
            creator_level_id = leave.user.level_id
            creator_name = leave.user.name
            creator_department_id = leave.user.department_id
            is_permit = leave.request_type == 'Permiso'

            if department_id == self.management_dep:
                # Avisar creador
                self.push_service.send_to_user(
                    user_id=creator_id,
                    title="Permiso rechazado" if is_permit else "Vacaciones rechazadas",
                    body=f"Tu solicitud de licencia LI-{leave.id} fue rechazada por Gerencia. Revisa el detalle.",
                )

                if creator_level_id != self.leader_lvl:
                    leader, lc = self.user_repository.get_leader(creator_department_id)
                    if lc != 200:
                        return leader, lc
                    
                    # Avisar leader
                    self.push_service.send_to_user(
                        user_id=leader.id,
                        title="La soclicitud se rechazó",
                        body=f"Gerencia rechazó la solicitud de licencia LI-{leave.id} de {format_name(creator_name, True)}. Revisa el detalle.",
                    )
            elif level_id in [self.leader_lvl, self.admin_lvl]:
                # Avisar creador
                self.push_service.send_to_user(
                    user_id=creator_id,
                    title="Solicitud rechazada",
                    body=f"{format_name(user_name, True)} rechazó tu solicitud de licencia LI-{leave.id}. Revisa el detalle.",
                )

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
