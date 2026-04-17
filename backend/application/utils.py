import logging, os, secrets
from datetime import datetime, timezone, timedelta, timezone, date, time


def generate_otp(length=6):
    return ''.join([str(secrets.randbelow(10)) for _ in range(length)])


def upload_path(path):
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        logging.exception("Could not create folder: %s", path)
        raise
    return path


def size(n):
    if n is None:
        return ""
    n = float(n)
    for unit in ["B","KB","MB","GB"]:
        if n < 1024:
            return f"{n:.0f}{unit}"
        n /= 1024
    return f"{n:.0f}TB"


def file_extension(filename):
        return (filename.rsplit(".", 1)[-1] if "." in filename else "").lower()


def allowed_extension(filename):
    allowed = {
        "pdf", "xml", "txt",
        "doc", "docx",
        "xls", "xlsx",
        "png", "jpg", "jpeg", "webp", "gif"
    }
    return file_extension(filename) in allowed


def peru_time():
    return datetime.now(timezone.utc) - timedelta(hours=5)


def parse_time(hhmm):
    return datetime.strptime(hhmm, "%H:%M").time()


def parse_date_iso(iso):
    return datetime.strptime(iso, "%Y-%m-%d").date()


def format_name(full_name, simple=False):
    if not full_name:
        return "Usuario"

    words = [w for w in full_name.strip().split() if w]
    n = len(words)

    if n == 0:
        return "Usuario"
    if simple:
        return words[0]
    
    if n == 1:
        return words[0]
    if n == 2:
        return f"{words[0]} {words[1]}"
    if 3 <= n <= 5:
        return f"{words[0]} {words[-2]}"

    return "Usuario"


def format_datetime(dt, simple=False):
    meses_cortos = ["ene", "feb", "mar", "abr", "may", "jun","jul", "ago", "sep", "oct", "nov", "dic"]
    if not dt:
        return ""

    if isinstance(dt, str):
        s = dt.replace("Z", "") 
        try:
            dt = datetime.fromisoformat(s)
        except Exception:
            return ""

    if getattr(dt, "tzinfo", None) is not None:
        dt = dt.replace(tzinfo=None)

    hora = dt.strftime("%I:%M %p").lower().lstrip("0")
    if simple:
        return hora
    return f"{dt.day} {meses_cortos[dt.month-1].title()}, {hora}"


def format_date(d):
    meses_largos = ["ene", "feb", "mar", "abr", "may", "jun","jul", "ago", "sep", "oct", "nov", "dic"]
    if not d:
        return ""

    if isinstance(d, str):
        s = d.replace("Z", "")
        try:
            if len(s) == 10:
                d = datetime.strptime(s, "%Y-%m-%d").date()
            else:
                d = datetime.fromisoformat(s).date()
        except Exception:
            return ""

    if isinstance(d, datetime):
        d = d.date()

    if not isinstance(d, date):
        return ""

    return f"{d.day} {meses_largos[d.month - 1].title()} {d.year}"


def format_time(t, seconds=False):
    if not t:
        return ""

    # String
    if isinstance(t, str):
        s = t.strip().replace("Z", "")
        try:
            # 'HH:MM' o 'HH:MM:SS'
            if len(s) in (5, 8) and s[2] == ":":
                fmt = "%H:%M:%S" if len(s) == 8 else "%H:%M"
                t = datetime.strptime(s, fmt).time()
            else:
                # ISO datetime
                t = datetime.fromisoformat(s).time()
        except Exception:
            return ""

    # Datetime -> time
    if isinstance(t, datetime):
        t = t.time()

    if not isinstance(t, time):
        return ""

    fmt = "%I:%M:%S %p" if seconds else "%I:%M %p"
    return t.strftime(fmt).lower().lstrip("0")


def calculate_passed_days(start_date):
    holidays = [
        "2026-01-01", "2026-04-02", "2026-04-03", "2026-04-05",
        "2026-05-01", "2026-06-29", "2026-07-28", "2026-07-29",
        "2026-08-30", "2026-10-08", "2026-11-01", "2026-12-08",
        "2026-12-25"
    ]
    
    tday = (datetime.today() - timedelta(hours=5)).date()
    current = start_date.date() if isinstance(start_date, datetime) else start_date
    passed_days = 0

    while current < tday:
        if current.weekday() < 5 and current.strftime('%Y-%m-%d') not in holidays:
            passed_days += 1
        current += timedelta(days=1)
    
    return passed_days

    