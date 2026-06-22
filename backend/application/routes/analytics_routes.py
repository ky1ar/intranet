from flask import Blueprint, request
from application.controllers.analytics_controller import AnalyticsController
from flask_jwt_extended import jwt_required


analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")
controller = AnalyticsController()


@analytics_bp.route("/screen", methods=["POST"])
@jwt_required()
def analytics_screen():
    return controller.log_screen(request.get_json())
