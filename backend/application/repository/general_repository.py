from datetime import date, datetime, timezone, timedelta
from application.handlers import handle_db_exceptions
from application.models import ServiceStatus, ServiceMethod, Users, TrackingAgencies, ShippingDistricts, ShippingMethod, TrackingStatus, BoardPriority, BoardStatuses, ServiceOrigin
from flask import g


class GeneralRepository:
    @handle_db_exceptions
    def get_service_status(self, full=None):
        query = g.db_session.query(ServiceStatus).order_by(ServiceStatus.id)

        if not full:
            query = query.filter(ServiceStatus.id != 9)
        service_status = query.all()

        if not service_status:
            return [], 400
        return service_status, 200


    @handle_db_exceptions
    def get_service_methods(self):
        service_methods = g.db_session.query(ServiceMethod).order_by(ServiceMethod.name).all()
        if not service_methods:
            return [], 400
        
        return service_methods, 200
    

    @handle_db_exceptions
    def get_service_origin(self):
        service_origin = g.db_session.query(ServiceOrigin).order_by(ServiceOrigin.name).all()
        if not service_origin:
            return [], 400
        
        return service_origin, 200


    @handle_db_exceptions
    def get_agencies(self):
        agencies = g.db_session.query(TrackingAgencies).order_by(TrackingAgencies.name).all()
        
        if not agencies:
            return [], 400
        return agencies, 200


    @handle_db_exceptions
    def get_tracking_status(self):
        agencies = g.db_session.query(TrackingStatus).filter(TrackingStatus.id != 4).order_by(TrackingStatus.id).all()
        
        if not agencies:
            return [], 400
        return agencies, 200
    
    
    @handle_db_exceptions
    def get_drivers(self):
        drivers = g.db_session.query(Users).filter_by(shipping_app_level=4).all()
        if not drivers:
            return 'Drivers not found', 404
        return drivers, 200


    @handle_db_exceptions
    def get_vendors(self):
        vendors = g.db_session.query(Users).filter((Users.level_id == 3) | (Users.department_id.in_([3, 7]))).order_by(Users.name).all()
        if not vendors:
            return 'Vendors not found', 400
        return vendors, 200


    @handle_db_exceptions
    def get_districts(self):
        #cache_key = "district:list"

        #cached = redis_client.get(cache_key)
        #if cached:
        #    logging.info('From redis')
        #    return json.loads(cached), 200 
        
        districts = g.db_session.query(ShippingDistricts).order_by(ShippingDistricts.name).all()
        if not districts:
            return 'Districts not found', 400
        return districts, 200


    @handle_db_exceptions
    def get_shipping_types(self):
        shipping_types = g.db_session.query(ShippingMethod).all()
        if not shipping_types:
            return 'Shipping Types not found', 400
        
        return shipping_types, 200
        

    @handle_db_exceptions
    def get_technicians(self):
        vendors = g.db_session.query(Users).filter(Users.department_id == 5).order_by(Users.name).all()
        
        if not vendors:
            return [], 400
        return vendors, 200
    

    @handle_db_exceptions
    def get_board_priority(self):
        priority = (g.db_session.query(BoardPriority).all())
        if not priority:
            return [], 404

        return priority, 200
    

    @handle_db_exceptions
    def get_board_statuses(self):
        statuses = (g.db_session.query(BoardStatuses).all())
        if not statuses:
            return [], 404

        return statuses, 200
    