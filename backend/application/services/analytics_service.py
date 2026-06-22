from application.handlers import handle_exceptions
from application.repository.analytics_repository import AnalyticsRepository
from flask_jwt_extended import get_jwt_identity


class AnalyticsService:
    def __init__(self):
        self.repository = AnalyticsRepository()

    @handle_exceptions
    def log_screen(self, route):
        user_id = int(get_jwt_identity())

        if not route or not isinstance(route, str):
            return "Ruta invalida", 400

        route = route.strip()[:255]
        if not route:
            return "Ruta invalida", 400

        return self.repository.log_visit(user_id, route)
