from application.handlers import handle_db_exceptions
from application.models import Machines, Brands
from sqlalchemy import func
from flask import g


class MachineRepository:
    @handle_db_exceptions
    def get_machines(self, machine_name):
        search_term = f"%{machine_name}%"
        full_name = func.concat(Brands.name, ' ', Machines.model).label("full_name")

        machines = (
            g.db_session.query(Machines.id, Machines.image, Machines.category_id, full_name)
            .join(Brands)
            .filter(full_name.ilike(search_term))
            .filter(Machines.category_id != 57)
            .order_by(full_name)
            .all()
        )
        if not machines:
            return None, 400

        return machines, 200
    

    @handle_db_exceptions
    def get_machine(self, machine_id):
        full_name = func.concat(Brands.name, ' ', Machines.model).label("full_name")
        machine = (
            g.db_session.query(Machines.id, Machines.image, full_name)
            .join(Brands)
            .filter(Machines.id == machine_id)
            .first()
        )
        if not machine:
            return None, 400

        return machine, 200
