import logging
from datetime import datetime, timedelta, date, timezone
from calendar import monthrange
from application.handlers import handle_exceptions
from application.repository.purchase_repository import PurchaseRepository
from application import socketio, redis_client
from flask_jwt_extended import get_jwt_identity


class PurchaseService:
    def __init__(self):
        self.purchase_repository = PurchaseRepository()


    @handle_exceptions
    def process(self, data):
        title = data.get("title", "").strip()
        if not title:
            return "Ingresa un título", 422

        new_purchase_id, aec = self.purchase_repository.add_purchase(data)
        if aec != 200:
            return new_purchase_id, aec
        
        # socketio.emit("calendar_update_dashboard", {})

        # event, ec = self.schedule_repository.get_event_by_id(new_event_id)
        # if ec == 200:
        #     creator_id = event.user_id
        #     creator_dept, _ = self.user_repository.get_user_department_id(creator_id)
        #     audience = self._audience_for_visibility(event.visibility_id or 1, creator_id, creator_dept)
        #     self._notify_bulk(audience, event, "created")
            
        return "Solicitud registrada correctamente", 200
    

    @handle_exceptions
    def requests(self):
        purchase_requests, prc = self.purchase_repository.get_purchase_requests()
        if prc != 200:
            return purchase_requests, prc
        
        purchase_requests_list = [
            {
                "id": purchase.id,
                "requester_name": purchase.user.name,
                "title": purchase.title,
                "reason": purchase.reason,
                "urgency_id": purchase.urgency_id,
                "quantity": purchase.quantity,
                "price": purchase.price,
                "needed_date": purchase.needed_date,
                "express": purchase.express,
                "status": purchase.status,
                "created_at": purchase.created_at,
                "department_approved_at": purchase.department_approved_at,
                "approved_at": purchase.approved_at,

            } for purchase in purchase_requests
        ]
        return purchase_requests_list, 200


    @handle_exceptions
    def type_options(self):
        purchase_type, ptc = self.purchase_repository.get_purchase_type()
        if ptc != 200:
            return purchase_type, ptc
        
        purchase_type_list = [
            {
                "id": option.id,
                "name": option.name,
                "slug": option.slug,

            } for option in purchase_type
        ]
        return purchase_type_list, 200
    

    @handle_exceptions
    def type_options(self):
        purchase_type, ptc = self.purchase_repository.get_purchase_type()
        if ptc != 200:
            return purchase_type, ptc
        
        purchase_type_list = [
            {
                "id": option.id,
                "name": option.name,
                "slug": option.slug,

            } for option in purchase_type
        ]
        return purchase_type_list, 200
    
    
    @handle_exceptions
    def urgency_options(self):
        urgency, uc = self.purchase_repository.get_urgency()
        if uc != 200:
            return urgency, uc
        
        urgency_list = [
            {
                "id": option.id,
                "name": option.name,
                "slug": option.slug,

            } for option in urgency
        ]
        return urgency_list, 200

    