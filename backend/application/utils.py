import logging
from datetime import datetime, timezone, timedelta, timezone, date


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
    meses_cortos = ["ene.", "feb.", "mar.", "abr.", "may.", "jun.","jul.", "ago.", "sep.", "oct.", "nov.", "dic."]
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
    return f"{dt.day} de {meses_cortos[dt.month-1]} a las {hora}"


def format_date(d):
    meses_largos = ["enero", "febrero", "marzo", "abril", "mayo", "junio","julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
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

    return f"{d.day} de {meses_largos[d.month - 1]}"