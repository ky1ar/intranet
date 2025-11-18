import logging
from decimal import Decimal
from datetime import datetime, timedelta, date, timezone
from calendar import monthrange
from application.handlers import handle_exceptions
from application.utils import format_name, format_datetime
from application.repository.purchase_repository import PurchaseRepository
from application.repository.user_repository import UserRepository
from application import socketio, redis_client
from flask_jwt_extended import get_jwt_identity


class PurchaseService:
    def __init__(self):
        self.purchase_repository = PurchaseRepository()
        self.user_repository = UserRepository()
        self.management_department = 7


    @handle_exceptions
    def process(self, data):
        new_purchase_id, aec = self.purchase_repository.add_purchase(data)
        if aec != 200:
            return new_purchase_id, aec
        
        socketio.emit("purchase_update_dashboard", {})

        # event, ec = self.schedule_repository.get_event_by_id(new_event_id)
        # if ec == 200:
        #     creator_id = event.user_id
        #     creator_dept, _ = self.user_repository.get_user_department_id(creator_id)
        #     audience = self._audience_for_visibility(event.visibility_id or 1, creator_id, creator_dept)
        #     self._notify_bulk(audience, event, "created")
            
        return "Solicitud registrada correctamente", 200
    

    @handle_exceptions
    def get(self, purchase_id):
        purchase, code = self.purchase_repository.get_purchase_by_id(purchase_id)
        if code != 200:
            return purchase, code

        user_id = int(get_jwt_identity())
        user, uc = self.user_repository.get_user_by_id(user_id)
        if uc != 200:
            return user, uc
        
        user_level = user.level_id
        user_department = user.department_id
        user_image = user.image
        editable = True
        can_approve = True

        if user_level == 2:
            leader, lc = self.user_repository.get_leader(user_department)
            if lc != 200:
                return leader, lc
            
            leader_image = leader.image
            can_approve = False

            if purchase.status_id > 1:
                editable = False

        elif user_level == 3:
            leader_image = user_image
            if purchase.status_id > 1:
                can_approve = False

            if purchase.status_id > 2:
                editable = False

        else:
            requester, uc = self.user_repository.get_user_by_id(purchase.user_id)
            if uc != 200:
                return requester, uc
            
            leader, lc = self.user_repository.get_leader(requester.department_id)
            if lc != 200:
                return leader, lc
            
            leader_image = leader.image
                #editable = False
            
        # can_approve = False
        # if user_level == 4:
        #     can_approve = True
        # elif user_level == 3 and purchase.user_id != user_id:
        #     can_approve = True
        
        # editable = False
        # if purchase.status_id == 1:
        #     editable = True
        # elif purchase.status_id == 2:
        #     if user_level == 3:
        #         editable = True
        #     else:
        #         editable = False

        dto = {
            "id": purchase.id,
            "editable": editable,
            "type_id": purchase.type_id,
            "can_approve": can_approve,
            "urgency_id": purchase.urgency_id,
            "express": bool(purchase.express),
            "needed_date": purchase.needed_date.isoformat() if purchase.needed_date else None,
            "user_comment": purchase.user_comment,
            "user_image": purchase.user.image,
            "leader_image": leader_image,
            "leader_comment": purchase.leader_comment,
            "total_items": purchase.total_items,
            "total_amount": float(purchase.total_amount) if purchase.total_amount is not None else None,
            "status_name": purchase.status.name,
            "status_slug": purchase.status.slug,
            "status_id": purchase.status_id,
            "items": [],
        }

        for item in purchase.items:
            if item.deleted_at:
                continue
            dto["items"].append({
                "id": item.id,
                "title": item.title,
                "description": item.description,
                "quantity": item.quantity,
                "price": float(item.price) if item.price is not None else None,
                "url": item.url,
                "ruc": item.ruc,
            })

        return dto, 200
    

    @handle_exceptions
    def update(self, data):
        result, code = self.purchase_repository.update_purchase(data)
        if code != 200:
            return result, code
        socketio.emit("purchase_update_dashboard", {})

        return "Solicitud actualizada correctamente", 200


    @handle_exceptions
    def requests(self):
        user_id = int(get_jwt_identity())
        user, uc = self.user_repository.get_user_by_id(user_id)
        if uc != 200:
            return user, uc
        
        if user.level_id == 4:
            visibility = []
        elif user.level_id == 3:
            user_ids, uic = self.user_repository.get_user_ids_by_department(user_id)
            if uic != 200:
                return user_ids, uic
            visibility = user_ids
        else:
            visibility = [user_id]

        purchase_requests, prc = self.purchase_repository.get_purchase_requests(visibility)
        if prc != 200:
            return purchase_requests, prc
        
        purchase_requests_list = [
            {
                "id": purchase.id,
                "requester_name": format_name(purchase.user.name) if user_id != purchase.user_id else 'Tú',
                "requester_department": purchase.user.department.name,
                "requester_image": purchase.user.image,
                "type_name": purchase.purchase_type.name,
                "user_comment": purchase.user_comment,
                "urgency_name": purchase.purchase_urgency.name,
                "express": purchase.express,
                "status_name": purchase.status.name,
                "status_slug": purchase.status.slug,
                "created_at": format_datetime(purchase.created_at),

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

    