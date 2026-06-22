from flask import Blueprint, request
from application.controllers.training_controller import TrainingController

training_bp = Blueprint("training", __name__, url_prefix="/training")
controller = TrainingController()


@training_bp.route("/calendar", methods=["GET"])
def training_calendar():
    offset = request.args.get('offset', None)
    return controller.training_calendar(offset)


@training_bp.route("/id/<training_id>", methods=["GET"])
def get_training_by_id(training_id):
    return controller.training_get_by_id(training_id)
