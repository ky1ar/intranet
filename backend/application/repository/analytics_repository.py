from application.handlers import handle_db_exceptions
from application.db_models.analytics_model import AuditRoute, AuditAttendanceMonitor
from flask import g


class AnalyticsRepository:

    @handle_db_exceptions
    def log_visit(self, user_id, route):
        view = AuditRoute(user_id=user_id, route=route)
        g.db_session.add(view)
        g.db_session.commit()
        return True, 200

    @handle_db_exceptions
    def log_profile_view(self, viewer_id, target_user_id):
        view = AuditAttendanceMonitor(viewer_id=viewer_id, target_user_id=target_user_id)
        g.db_session.add(view)
        g.db_session.commit()
        return True, 200
