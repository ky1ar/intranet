import re
from application.handlers import handle_exceptions
from application.repository.analytics_repository import AnalyticsRepository
from flask_jwt_extended import get_jwt_identity


def simplify_user_agent(ua):
    if not ua:
        return None

    # --- Sistema operativo ---
    if "iPhone" in ua or "iPad" in ua or "iPhone OS" in ua:
        os_name = "iOS"
    elif "Android" in ua:
        os_name = "Android"
    elif "Windows NT" in ua:
        os_name = "Windows"
    elif "Mac OS X" in ua or "Macintosh" in ua:
        os_name = "macOS"
    elif "Linux" in ua:
        os_name = "Linux"
    else:
        os_name = "Otro"

    # --- Navegador (orden importa: Edge/Opera comparten token con Chrome) ---
    if m := re.search(r"Edg(?:A|iOS)?/(\d+)", ua):
        browser = f"Edge {m.group(1)}"
    elif m := re.search(r"(?:OPR|Opera)/(\d+)", ua):
        browser = f"Opera {m.group(1)}"
    elif m := re.search(r"SamsungBrowser/(\d+)", ua):
        browser = f"Samsung Internet {m.group(1)}"
    elif m := re.search(r"Firefox/(\d+)", ua):
        browser = f"Firefox {m.group(1)}"
    elif "Chrome/" in ua and (m := re.search(r"Chrome/(\d+)", ua)):
        browser = f"Chrome {m.group(1)}"
    elif "Safari/" in ua and (m := re.search(r"Version/(\d+)", ua)):
        browser = f"Safari {m.group(1)}"
    else:
        browser = "Otro"

    return f"{os_name} / {browser}"


class AnalyticsService:
    def __init__(self):
        self.repository = AnalyticsRepository()

    @handle_exceptions
    def log_screen(self, route, device_id=None, ip=None, user_agent=None):
        user_id = int(get_jwt_identity())

        if not route or not isinstance(route, str):
            return "Ruta invalida", 400

        route = route.strip()[:255]
        if not route:
            return "Ruta invalida", 400

        device_id = (device_id or "").strip()[:64] or None
        ip = (ip or "").strip()[:64] or None
        user_agent = simplify_user_agent(user_agent)

        return self.repository.log_visit(user_id, route, device_id, ip, user_agent)
