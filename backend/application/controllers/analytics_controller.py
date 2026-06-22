from flask import request
from application.handlers import handle_logs_and_exceptions, validate_request
from application.services.analytics_service import AnalyticsService


class AnalyticsController:
    def __init__(self):
        self.analytics = AnalyticsService()

    @handle_logs_and_exceptions
    def log_screen(self, data):
        if validation := validate_request(data, {"route"}):
            return validation, 400

        forwarded = request.headers.get("X-Forwarded-For") or request.remote_addr or ""
        ip = forwarded.split(",")[0].strip()
        user_agent = request.headers.get("User-Agent", "")

        return self.analytics.log_screen(
            data.get("route"),
            data.get("device_id"),
            ip,
            user_agent,
        )
