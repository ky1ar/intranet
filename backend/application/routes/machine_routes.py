from flask import Blueprint, request
from application.controllers.machine_controller import MachineController


machine_bp = Blueprint("machine", __name__, url_prefix="/machine")
controller = MachineController()


@machine_bp.route("/find/<machine_name>", methods=["GET"])
def machine_find_machines(machine_name):
    return controller.machine_find_machines(machine_name)

