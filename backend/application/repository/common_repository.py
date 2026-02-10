from datetime import date, datetime, timezone, timedelta
from application.handlers import handle_db_exceptions
from application.models import Users, Department, Province, District
from flask import g


class CommonRepository:
    @handle_db_exceptions
    def get_vendors(self):
        vendors = (
            g.db_session.query(Users)
            .filter(Users.department_id == 3)
            .filter(Users.level_id != 1)
            .filter(Users.level_id != 5)
            .order_by(Users.name)
            .all()
        )
        
        if not vendors:
            return [], 400
        return vendors, 200


    @handle_db_exceptions
    def get_workers(self):
        workers = (
            g.db_session.query(Users)
            .filter(Users.department_id != 7)
            .filter(Users.document != "00000000")
            .filter(Users.level_id != 1)
            .filter(Users.level_id != 5)
            .order_by(Users.name)
            .all()
        )
        
        if not workers:
            return [], 400
        return workers, 200


    @handle_db_exceptions
    def get_departments(self):
        departments = (
            g.db_session.query(Department)
            .order_by(Department.name)
            .all()
        )
        
        if not departments:
            return [], 400
        return departments, 200
    

    @handle_db_exceptions
    def get_provinces(self, department_id):
        provinces = (
            g.db_session.query(Province)
            .filter(Province.department_id == department_id)
            .order_by(Province.name)
            .all()
        )
        
        if not provinces:
            return [], 400
        return provinces, 200
    

    @handle_db_exceptions
    def get_districts(self, province_id):
        districts = (
            g.db_session.query(District)
            .filter(District.province_id == province_id)
            .order_by(District.name)
            .all()
        )
        
        if not districts:
            return [], 400
        return districts, 200