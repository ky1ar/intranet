from application.handlers import handle_exceptions
from application.repository.analytics_repository import AnalyticsRepository
from flask_jwt_extended import get_jwt_identity


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
        user_agent = (user_agent or "").strip()[:255] or None

        return self.repository.log_visit(user_id, route, device_id, ip, user_agent)
