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


    def _time_to_minutes(self, t):
        hh, mm = t.split(":")
        return int(hh) * 60 + int(mm)


    def _normalize_times(self, times, window_minutes=5):
        out = []
        last_min = None

        for t in times:
            t = (t or "").strip()
            if not t:
                continue

            try:
                cur = self._time_to_minutes(t)
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
        user_id = data.get("user_id")
        offset = data.get("offset")

        period, pc = self.attendance_repository.get_period_by_offset(offset, today=date.today())
        if pc != 200:
            return period, pc

        if not period:
            return {"period": None, "weeks": []}, 200

        payload, rc = self.attendance_repository.build_period_summary(int(user_id), period)
        return payload, rc
