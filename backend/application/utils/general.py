import logging
from datetime import datetime, timezone, timedelta, timezone


def peru_time():
    return datetime.now(timezone.utc) - timedelta(hours=5)