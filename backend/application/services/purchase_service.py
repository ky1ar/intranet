import logging
from application.handlers import handle_exceptions
from application.utils import format_name, format_datetime
from application.services.push_service import PushSender
from application.repository.purchase_repository import PurchaseRepository
from application.repository.user_repository import UserRepository
from application import socketio
from flask_jwt_extended import get_jwt_identity


class PurchaseService:
    def __init__(self):
        self.purchase_repository = PurchaseRepository()
        self.user_repository = UserRepository()
        self.push_service = PushSender()
        self.management_department = 7
        self.worker_level = 2
        self.leader_level = 3
        self.management_level = 4


    @handle_exceptions
    def process(self, data):
        user_id = int(get_jwt_identity())
        user, uc = self.user_repository.get_user_by_id(user_id)
        if uc != 200:
            return user, uc

        new_purchase_id, aec = self.purchase_repository.add_purchase(data, user)
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
    def get_request(self, purchase_id):
        purchase, code = self.purchase_repository.get_purchase_by_id(purchase_id)
        if code != 200:
            return purchase, code

        user_id = int(get_jwt_identity())
        user, uc = self.user_repository.get_user_by_id(user_id)
        if uc != 200:
            return user, uc
        
        user_level_id = user.level_id

        if user_level_id == self.worker_level:
            return self._get_worker_request(user, purchase)

        if user_level_id == self.leader_level:
            return self._get_leader_request(user, purchase)
        
        return self._get_manager_request(user, purchase)
    

    @handle_exceptions
    def _get_worker_request(self, user, purchase):
        status_id = purchase.status_id
        leader = None
        manager = None

        if status_id > 1:
            leader, lc = self.user_repository.get_leader(user.department_id)
            if lc != 200:
                return leader, lc
        
        if status_id > 2:
            manager, lc = self.user_repository.get_manager()
            if lc != 200:
                return manager, lc
            
        modal = {
            1: "edit",
        }
        dto = {
            "modal": modal.get(status_id, "view"),
            "id": purchase.id,
            "pr": f"PR-{purchase.id:04d}",
            "type_id": purchase.type_id,
            "urgency_id": purchase.urgency_id,
            "express": bool(purchase.express),
            "it_validation": bool(purchase.it_validation),
            "needed_date": purchase.needed_date.isoformat() if purchase.needed_date else None,
            "status_name": purchase.status.name,
            "status_slug": purchase.status.slug,
            "status_id": status_id,
            "self_created": True if user.id == purchase.user.id else False,
            
            "user_name": format_name(purchase.user.name),
            "created_at": format_datetime(purchase.created_at),

            "items": [],
            "chats": [],
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
                "order_number": item.order_number,
            })
        
        for chat in purchase.chats:
            dto["chats"].append({
                "id": chat.id,
                "comment": chat.comment,
                "commenter_id": chat.commenter_id,
                "commenter_name": format_name(chat.commenter.name),
                "commenter_image": chat.commenter.image,
                "created_at": format_datetime(chat.created_at),
            })

        return dto, 200
    

    @handle_exceptions
    def _get_leader_request(self, user, purchase):
        status_id = purchase.status_id
        manager = None
        
        if status_id > 2:
            manager, lc = self.user_repository.get_manager()
            if lc != 200:
                return manager, lc
        
        modal = {
            1: "approve",
            2: "delete",
        }
        dto = {
            "modal": modal.get(status_id, "view"),
            "id": purchase.id,
            "pr": f"PR-{purchase.id:04d}",
            "type_id": purchase.type_id,
            "urgency_id": purchase.urgency_id,
            "express": bool(purchase.express),
            "it_validation": bool(purchase.it_validation),
            "needed_date": purchase.needed_date.isoformat() if purchase.needed_date else None,
            "status_name": purchase.status.name,
            "status_slug": purchase.status.slug,
            "status_id": status_id,
            "self_created": True if user.id == purchase.user.id else False,

            "user_name": format_name(purchase.user.name),
            "created_at": format_datetime(purchase.created_at),

            "items": [],
            "chats": [],
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
                "order_number": item.order_number,
            })

        for chat in purchase.chats:
            dto["chats"].append({
                "id": chat.id,
                "comment": chat.comment,
                "commenter_id": chat.commenter_id,
                "commenter_name": format_name(chat.commenter.name),
                "commenter_image": chat.commenter.image,
                "created_at": format_datetime(chat.created_at),
            })

        return dto, 200
    

    @handle_exceptions
    def _get_manager_request(self, user, purchase):
        status_id = purchase.status_id
        leader = None
        
        if status_id > 1:
            leader, lc = self.user_repository.get_leader(purchase.user.department_id)
            if lc != 200:
                return leader, lc
            
        modal = {
            1: "approve",
            2: "approve",
        }
        dto = {
            "modal": modal.get(status_id, "view"),
            "id": purchase.id,
            "pr": f"PR-{purchase.id:04d}",
            "type_id": purchase.type_id,
            "urgency_id": purchase.urgency_id,
            "express": bool(purchase.express),
            "it_validation": bool(purchase.it_validation),
            "needed_date": purchase.needed_date.isoformat() if purchase.needed_date else None,
            "status_name": purchase.status.name,
            "status_slug": purchase.status.slug,
            "status_id": status_id,
            "self_created": True if user.id == purchase.user.id else False,

            "user_name": format_name(purchase.user.name),
            "created_at": format_datetime(purchase.created_at),

            "items": [],
            "chats": [],
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
                "order_number": item.order_number,
            })

        for chat in purchase.chats:
            dto["chats"].append({
                "id": chat.id,
                "comment": chat.comment,
                "commenter_id": chat.commenter_id,
                "commenter_name": format_name(chat.commenter.name),
                "commenter_image": chat.commenter.image,
                "created_at": format_datetime(chat.created_at),
            })

        return dto, 200


    @handle_exceptions
    def update(self, data):
        user_id = int(get_jwt_identity())
        user, uc = self.user_repository.get_user_by_id(user_id)
        if uc != 200:
            return user, uc

        action = data.get("action")

        if data.get("delete") is True:
            result, code = self.purchase_repository.soft_delete(data["purchase_id"])
            if code != 200:
                return result, code

        elif action == "progress":
            result, code = self.purchase_repository.set_status(
                data["purchase_id"], status_id=4
            )
            if code != 200:
                return result, code
            
        elif action == "payed":
            result, code = self.purchase_repository.set_status(
                data["purchase_id"], status_id=5
            )
            if code != 200:
                return result, code
        
        elif action == "invoiced":
            result, code = self.purchase_repository.set_status(
                data["purchase_id"], status_id=6
            )
            if code != 200:
                return result, code
            
        elif action == "reject":
            result, code = self.purchase_repository.set_status(
                data["purchase_id"], status_id=10
            )
            if code != 200:
                return result, code

        elif action == "approve":
            result, code = self.purchase_repository.update_purchase(data)
            if code != 200:
                return result, code

            status_id = None
            if user.level_id == self.leader_level:
                status_id = 2
            elif user.level_id == self.management_level:
                status_id = 3
            else:
                return "No autorizado para aprobar", 403

            result, code = self.purchase_repository.set_status(
                data["purchase_id"], status_id
            )
            if code != 200:
                return result, code

        else:
            result, code = self.purchase_repository.update_purchase(data)
            if code != 200:
                return result, code

        socketio.emit("purchase_update_dashboard", {})
        return "Solicitud actualizada correctamente", 200


    @handle_exceptions
    def _get_worker_request_list(self, user_id):
        purchase_requests, prc = self.purchase_repository.get_purchase_requests([user_id])
        if prc != 200:
            return purchase_requests, prc
        
        return self._format_requests_reponse(purchase_requests, user_id, self.worker_level)


    @handle_exceptions
    def _get_leader_request_list(self, user_id):
        department_user_ids, duic = self.user_repository.get_user_ids_by_department(user_id)
        if duic != 200:
            return department_user_ids, duic
    
        purchase_requests, prc = self.purchase_repository.get_purchase_requests(department_user_ids)
        if prc != 200:
            return purchase_requests, prc
        
        return self._format_requests_reponse(purchase_requests, user_id, self.leader_level)

    
    @handle_exceptions
    def _get_manager_request_list(self, user_id):
        purchase_requests, prc = self.purchase_repository.get_purchase_requests([])
        if prc != 200:
            return purchase_requests, prc
        
        return self._format_requests_reponse(purchase_requests, user_id, self.leader_level)
    

    @handle_exceptions
    def _format_requests_reponse(self, purchase_requests, user_id, level):
        return {
            "requests": [
                {
                    "id": purchase.id,
                    "pr": f"PR-{purchase.id:04d}",
                    "requester_name": format_name(purchase.user.name) if user_id != purchase.user_id else 'Tú',
                    "requester_department": purchase.user.department.name,
                    "requester_image": purchase.user.image,
                    "type_name": purchase.purchase_type.name,
                    "urgency_name": purchase.purchase_urgency.name,
                    "express": purchase.express,
                    "status_name": purchase.status.name,
                    "status_slug": purchase.status.slug,
                    "created_at": format_datetime(purchase.created_at),

                } for purchase in purchase_requests
            ],
            "viewer_level_id": level,
        }, 200


    @handle_exceptions
    def requests(self):
        user_id = int(get_jwt_identity())
        user, uc = self.user_repository.get_user_by_id(user_id)
        if uc != 200:
            return user, uc
        
        user_level_id = user.level_id

        if user_level_id == self.worker_level:
            return self._get_worker_request_list(user_id)

        if user_level_id == self.leader_level and user_id != 1:
            return self._get_leader_request_list(user_id)
        
        return self._get_manager_request_list(user_id)
    
    
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

    
    @handle_exceptions
    def send_chat(self, data):
        if not data.get("purchase_id"):
            return "purchase_id requerido", 400

        comment = (data.get("comment") or "").strip()
        if not comment:
            return "Comentario vacío", 400

        user_id = int(get_jwt_identity())

        purchase, pc = self.purchase_repository.get_purchase_by_id(data["purchase_id"])
        if pc != 200:
            return purchase, pc

        chat, cc = self.purchase_repository.add_chat(
            purchase_id=purchase.id,
            user_id=user_id,
            comment=comment
        )
        if cc != 200:
            return chat, cc

        socketio.emit("purchase_update_dashboard", {})

        return {
            "id": chat.id,
            "comment": chat.comment,
            "commenter_id": chat.commenter_id,
            "commenter_name": format_name(chat.commenter.name),
            "commenter_image": chat.commenter.image,
            "created_at": format_datetime(chat.created_at),
        }, 200