import logging, os, re
import pandas as pd
from io import BytesIO
from datetime import datetime, timedelta, date
from application.handlers import handle_exceptions
from application.utils import parse_date_iso, parse_time
from application.repository.attendance_repository import AttendanceRepository
from application.repository.user_repository import UserRepository
from flask_jwt_extended import get_jwt_identity


_RE_DATE_RANGE = re.compile(r"(\d{4}-\d{2}-\d{2})\s*~\s*(\d{4}-\d{2}-\d{2})")
_RE_TIME = re.compile(r"\d{2}:\d{2}")
_RE_DNI = re.compile(r"\d{8}")


class AttendanceService:
    def __init__(self):
        self.attendance_repository = AttendanceRepository()
        self.user_repository = UserRepository()


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
    def summary_by_offset(self, data):
        user_id = int(data.get("user_id"))
        offset = int(data.get("offset") or 0)

        period, pc = self.attendance_repository.get_period_by_offset(offset, today=date.today())
        if pc != 200:
            return period, pc

        if not period:
            return {"period": None, "weeks": []}, 200

        # 1) payload base (marcas agrupadas)
        payload, rc = self.attendance_repository.build_period_summary(user_id, period)
        if rc != 200:
            return payload, rc

        # 2) perfil vigente para el rango (simplificación: asumimos que no cambia dentro del periodo)
        #    Si puede cambiar dentro del periodo, luego lo mejoramos con "por fecha".
        profile, prc = self.attendance_repository.get_profile_for_user_on_date(user_id, period.start_date)
        if prc != 200:
            return profile, prc

        # fallback si no tiene perfil asignado
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

        # 3) Enriquecer días + resumen semanal en domingo
        for w in payload.get("weeks", []):
            week_worked = 0
            week_target = 0
            week_incomplete = 0

            for day in w.get("days", []):
                dt = parse_date_iso(day["date"])  # date
                wd = dt.weekday()

                if wd == 6:  # domingo => resumen
                    day["is_summary"] = True
                    day["label"] = "Σ"
                    day["intervals"] = []
                    day["summary"] = {
                        "worked_min": week_worked,
                        "target_min": week_target,
                        "delta_min": week_worked - week_target,
                        "incomplete": week_incomplete,  # opcional
                    }
                    continue

                day["is_summary"] = False

                target = self._target_minutes_for_date(profile_map, dt)
                expected_start_min = self._expected_start_minutes_for_date(profile_map, dt)
                day["expected_start"] = self._minutes_to_hhmm(expected_start_min) if expected_start_min is not None else None

                worked = 0
                has_open_interval = False

                for it in (day.get("intervals") or []):
                    if it.get("start") and not it.get("end"):
                        has_open_interval = True
                    worked += self._interval_minutes(it)

                # ✅ campos por día
                day["target_min"] = target
                day["worked_min"] = worked
                day["incomplete"] = bool(has_open_interval)
                day["incomplete_count"] = 1 if has_open_interval else 0

                # ✅ el objetivo SIEMPRE cuenta para el resumen (lunes-sábado)
                week_target += target

                # ❗ día incompleto: NO delta, NO sumar worked a la semana
                if has_open_interval:
                    day["delta_min"] = None
                    week_incomplete += 1
                    continue

                # ✅ día completo: delta + sumar worked
                day["delta_min"] = worked - target
                week_worked += worked

        payload["profile"] = {"id": profile.id, "slug": profile.slug, "name": profile.name}
        return payload, 200


    