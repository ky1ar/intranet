import logging
from datetime import datetime, timezone, timedelta, timezone


def peru_time():
    return datetime.now(timezone.utc) - timedelta(hours=5)


def format_name(full_name):
    if not full_name:
        return "Usuario"

    words = [w for w in full_name.strip().split() if w]
    n = len(words)

    if n == 0:
        return "Usuario"
    if n == 1:
        return words[0]
    if n == 2:
        return f"{words[0]} {words[1]}"
    if 3 <= n <= 5:
        return f"{words[0]} {words[-2]}"

    return "Usuario"


def format_datetime(dt):
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
        return f"{dt.day} de {meses_cortos[dt.month-1]} a las {hora}"