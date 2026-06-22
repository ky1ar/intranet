from application.handlers import handle_db_exceptions
from application.db_models.analytics_model import AuditRoute, AuditAttendanceMonitor
from flask import g


class AnalyticsRepository:

    @handle_db_exceptions
    def log_visit(self, user_id, route, device_id=None, ip=None, user_agent=None):
        view = AuditRoute(
            user_id=user_id,
            route=route,
            device_id=device_id,
            ip=ip,
            user_agent=user_agent,
        )
        g.db_session.add(view)
        g.db_session.commit()
        return True, 200

    @handle_db_exceptions
    def log_profile_view(self, viewer_id, target_user_id):
        view = AuditAttendanceMonitor(viewer_id=viewer_id, target_user_id=target_user_id)
        g.db_session.add(view)
        g.db_session.commit()
        return True, 200
