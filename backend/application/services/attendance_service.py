import logging, os, re
import pandas as pd
from io import BytesIO
from datetime import datetime, timedelta, date
from application.handlers import handle_exceptions
from application.utils import parse_date_iso, parse_time, format_name, format_datetime
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
        self.management_dep = 7
        self.purchases_dep = 8
        self.worker_lvl = 2
        self.leader_lvl = 3
        self.admin_lvl = 4


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

        return self._normalize_times(compact, window_minutes=5)


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

        profile, prc = self.attendance_repository.get_profile_for_user_on_date(user_id, period.start_date)
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

        for w in payload.get("weeks", []):
            week_worked = 0
            week_target = 0
            week_incomplete = 0

            for day in w.get("days", []):
                dt = parse_date_iso(day["date"])
                wd = dt.weekday()

                shifts_for_day = (profile_map.get(wd) or [])
                day["expected_marks"] = len(shifts_for_day) * 2

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

                target = self._target_minutes_for_date(profile_map, dt)
                expected_start_min = self._expected_start_minutes_for_date(profile_map, dt)
                day["expected_start"] = self._minutes_to_hhmm(expected_start_min) if expected_start_min is not None else None

                week_target += target

                if day.get("is_holiday") and day.get("in_period"):
                    day["worked_min"] = target
                    day["target_min"] = target
                    day["delta_min"] = 0
                    day["incomplete"] = False
                    day["incomplete_count"] = 0

                    week_worked += target
                    continue

                worked = 0
                has_open_interval = False

                for it in (day.get("intervals") or []):
                    if it.get("start") and not it.get("end"):
                        has_open_interval = True
                    worked += self._interval_minutes(it)

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

        expected = self._expected_marks_for_user_on_date(user_id, d)

        if expected <= 0:
            return "Este día no requiere marcaciones.", 422

        existing, ec = self.attendance_repository.get_marks_by_user_and_date(user_id, d)
        if ec != 200:
            return existing, ec

        existing_times = [m.mark_at.strftime("%H:%M") for m in (existing or [])]

        if len(existing_times) >= expected:
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

            if pos < 0 or pos >= expected:
                return f"position fuera de rango: {pos}.", 422

            try:
                parse_time(t)
            except Exception:
                return f"Hora inválida: {t}.", 422

            if pos in add_positions:
                return f"position repetido: {pos}.", 422
            add_positions.add(pos)

            add_times.append((pos, t))

        final = [None] * expected

        for pos, t in add_times:
            final[pos] = t

        it = iter(existing_times)
        for i in range(expected):
            if final[i] is None:
                try:
                    final[i] = next(it)
                except StopIteration:
                    break

        if any(x is None for x in final):
            return "No alcanza para completar el día con esos datos.", 422

        if len(set(final)) != len(final):
            return "No se permiten horas duplicadas.", 422

        mins = []
        for hhmm in final:
            mins.append(self._hhmm_to_minutes(hhmm))
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
                "created_by": editor_user_id,  # ✅
            })

        res, rc = self.attendance_repository.insert_marks_with_meta(to_insert)
        if rc != 200:
            return res, rc

        return {
            "message": "Marcaciones completadas.",
            "expected_marks": expected,
            "inserted": res.get("inserted", 0),
            "final": final,
        }, 200
    

    @handle_exceptions
    def leave_request(self, data):
        user_id = int(data["user_id"])
        user, uc = self.user_repository.get_user_by_id(user_id)
        if uc != 200:
            return user, uc
        
        level_id = user.level_id
        d = parse_date_iso(data["date"])

        payload = {
            "user_id": user_id,
            "date": d,
            "duration_id": int(data["duration_id"]),
            "leave_type_id": int(data["leave_type_id"]),
            "leave_type_detail": (data.get("leave_type_detail") or "").strip(),
            "motive": (data.get("motive") or "").strip(),
            "recovery_plan": (data.get("recovery_plan") or "").strip(),
        }

        res, rc = self.attendance_repository.insert_leave_request(payload, level_id)
        if rc != 200:
            return res, rc
        socketio.emit("attendance_update_leaves", {})
        return "Permiso solicitado.", 200


    @handle_exceptions
    def vacation_request(self, data):
        user_id = int(data["user_id"])
        user, uc = self.user_repository.get_user_by_id(user_id)
        if uc != 200:
            return user, uc
        
        level_id = user.level_id
        start = parse_date_iso(data["start_date"])
        end = parse_date_iso(data["end_date"])
        if end < start:
            return "Rango inválido de fechas.", 422

        payload = {
            "user_id": user_id,
            "start_date": start,
            "end_date": end,
            "assigned_user_id": int(data["assigned_user_id"]),
            "description": (data.get("description") or "").strip(),
        }

        res, rc = self.attendance_repository.insert_vacation_request(payload, level_id)
        if rc != 200:
            return res, rc
        socketio.emit("attendance_update_leaves", {})
        return "Vacaciones solicitadas.", 200