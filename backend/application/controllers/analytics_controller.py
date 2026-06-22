from application.handlers import handle_logs_and_exceptions, validate_request
from application.services.analytics_service import AnalyticsService


class AnalyticsController:
    def __init__(self):
        self.analytics = AnalyticsService()

    @handle_logs_and_exceptions
    def log_screen(self, data):
        if validation := validate_request(data, {"route"}):
            return validation, 400
        return self.analytics.log_screen(data.get("route"))
