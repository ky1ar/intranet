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
        self.management_dep = 7
        self.purchases_dep = 8
        self.worker_lvl = 2
        self.leader_lvl = 3
        self.admin_lvl = 4


    @handle_exceptions
    def process(self, data):
        user_id = int(get_jwt_identity())
        logging.info(user_id)

        user, uc = self.user_repository.get_user_by_id(user_id)
        if uc != 200:
            return user, uc

        new_purchase_id, aec = self.purchase_repository.add_purchase(data, user)
        if aec != 200:
            return new_purchase_id, aec
        
        socketio.emit("purchase_update_dashboard", {})

        level_id = user.level_id
        department_id = user.department_id
        logging.info(level_id)
        logging.info(department_id)

        express = data.get("express")
        if department_id == self.management_dep:
            logging.info("Manager flow")
            user_ids, duic = self.user_repository.get_user_ids_by_department(department_id=self.purchases_dep)
            if duic != 200:
                return user_ids, duic
            user_ids.append(1) # Added Leslie

            self.push_service.send_to_users(
                user_ids=user_ids,
                title=f"Solicitud PR-{new_purchase_id} recibida",
                body="Hay una nueva solicitud de compra pendiente de gestión.",
            )
        
        elif level_id in [self.leader_lvl, self.admin_lvl]:
            logging.info("Leaders Flow")
            if express == 1:
                logging.info("Is Express")

                if department_id != 8:
                    department_user_ids, duic = self.user_repository.get_user_ids_by_department(department_id=self.purchases_dep)
                    if duic != 200:
                        return department_user_ids, duic
                    
                    department_user_ids.append(1)
                    logging.info(department_user_ids)
                    self.push_service.send_to_users(
                        user_ids=department_user_ids,
                        title=f"Solicitud PR-{new_purchase_id} recibida",
                        body="Hay una nueva solicitud de compra pendiente de gestión.",
                    )
            else:
                logging.info("Is classic")
                manager, mc = self.user_repository.get_manager()
                if mc != 200:
                    return manager, mc
                
                self.push_service.send_to_user(
                    user_id=manager.id,
                    title="Aprobación pendiente",
                    body=f"La solicitud de compra PR-{new_purchase_id} de {format_name(user.name, True)} necesita tu aprobación.",
                )
        else:
            logging.info("Worker flow")

            leader, lc = self.user_repository.get_leader(department_id)
            if lc != 200:
                return leader, lc
            logging.info(leader.id)
            
            self.push_service.send_to_user(
                user_id=leader.id,
                title="Aprobación pendiente",
                body=f"La solicitud de compra PR-{new_purchase_id} de {format_name(user.name, True)} necesita tu aprobación.",
            )
            
        return "Solicitud registrada correctamente", 200
    

    @handle_exceptions
    def get_request(self, purchase_id):
        purchase, pc = self.purchase_repository.get_purchase_by_id(purchase_id)
        if pc != 200:
            return purchase, pc

        user_id = int(get_jwt_identity())
        user, uc = self.user_repository.get_user_by_id(user_id)
        if uc != 200:
            return user, uc
        
        level_id = user.level_id
        department_id = user.department_id

        if department_id == self.management_dep:
            return self._get_manager_request(user, purchase)
        
        elif level_id in [self.leader_lvl, self.admin_lvl]:
            return self._get_leader_request(user, purchase)
        
        return self._get_worker_request(user, purchase)
    

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
            "pr": f"PR-{purchase.id}",
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
            "pr": f"PR-{purchase.id}",
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
            "pr": f"PR-{purchase.id}",
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
        purchase_id = data.get("purchase_id")
        
        if data.get("delete") is True:
            result, code = self.purchase_repository.soft_delete(purchase_id)
            if code != 200:
                return result, code

        elif action == "progress":
            result, code = self.purchase_repository.set_status(purchase_id, status_id=4)
            if code != 200:
                return result, code
            
            purchase, pc = self.purchase_repository.get_purchase_by_id(purchase_id)
            if pc != 200:
                return purchase, pc

            # Avisar creador
            self.push_service.send_to_user(
                user_id=purchase.user_id,
                title=f"Solicitud PR-{purchase.id} en progreso",
                body=f"Estamos procesando tu solicitud de compra.",
            )
            
        elif action == "payed":
            items = data.get("items") or []
            if items:
                result, code = self.purchase_repository.update_order_numbers(purchase_id, items)
                if code != 200:
                    return result, code

            result, code = self.purchase_repository.set_status(purchase_id, status_id=5)
            if code != 200:
                return result, code
            
            purchase, pc = self.purchase_repository.get_purchase_by_id(purchase_id)
            if pc != 200:
                return purchase, pc
            
            # Avisar creador
            self.push_service.send_to_user(
                user_id=1,
                title="Pago realizado",
                body=f"El pago de la solicitud PR-{purchase.id} ha sido confirmado.",
            )
        
        elif action == "invoiced":
            result, code = self.purchase_repository.set_status(purchase_id, status_id=6)
            if code != 200:
                return result, code
        
        elif action == "delivered":
            result, code = self.purchase_repository.set_status(purchase_id, status_id=7)
            if code != 200:
                return result, code
            
            purchase, pc = self.purchase_repository.get_purchase_by_id(purchase_id)
            if pc != 200:
                return purchase, pc

            # Avisar creador
            self.push_service.send_to_user(
                user_id=purchase.user_id,
                title="Entrega confirmada",
                body=f"Tu solicitud de compra PR-{purchase.id} ya fue entregada.",
            )
            
        elif action == "reject":
            result, code = self.purchase_repository.set_status(purchase_id, status_id=10)
            if code != 200:
                return result, code

            level_id = user.level_id
            department_id = user.department_id
            user_name = user.name

            purchase, pc = self.purchase_repository.get_purchase_by_id(purchase_id)
            if pc != 200:
                return purchase, pc

            creator_id = purchase.user_id
            creator_level_id = purchase.user.level_id

            if department_id == self.management_dep:
                # Avisar creador
                self.push_service.send_to_user(
                    user_id=creator_id,
                    title="Solicitud rechazada",
                    body=f"Tu solicitud de compra PR-{purchase.id} fue rechazada por Gerencia. Revisa el detalle.",
                )

                if creator_level_id != self.leader_lvl:
                    leader, lc = self.user_repository.get_leader(creator_department_id)
                    if lc != 200:
                        return leader, lc
                    
                    # Avisar leader
                    self.push_service.send_to_user(
                        user_id=leader.id,
                        title="Solicitud rechazada",
                        body=f"La solicitud de compra PR-{purchase.id} ha sido rechazada. Revisa el detalle.",
                    )
            elif level_id in [self.leader_lvl, self.admin_lvl]:
                # Avisar creador
                self.push_service.send_to_user(
                    user_id=creator_id,
                    title="Solicitud rechazada",
                    body=f"{format_name(user_name, True)} rechazó tu solicitud de compra PR-{purchase.id}. Revisa el detalle.",
                )

        elif action == "approve":
            update_purchase, upc = self.purchase_repository.update_purchase(data)
            if upc != 200:
                return update_purchase, upc

            level_id = user.level_id
            department_id = user.department_id
            user_name = user.name

            status_id = None
            if department_id == self.management_dep:
                status_id = 3
            elif level_id in [self.leader_lvl, self.admin_lvl]:
                status_id = 2
            else:
                return "No autorizado para aprobar", 403

            status, sc = self.purchase_repository.set_status(purchase_id, status_id)
            if sc != 200:
                return status, sc
            
            purchase, pc = self.purchase_repository.get_purchase_by_id(purchase_id)
            if pc != 200:
                return purchase, pc

            purchase_id = purchase.id
            creator_id = purchase.user_id
            creator_name = purchase.user.name
            creator_department_id = purchase.user.department_id
            creator_level_id = purchase.user.level_id
            express = purchase.express

            department_user_ids, duic = self.user_repository.get_user_ids_by_department(department_id=self.purchases_dep)
            if duic != 200:
                return department_user_ids, duic
            department_user_ids.append(1)

            if department_id == self.management_dep:
                # Avisar area de compras
                self.push_service.send_to_users(
                    user_ids=department_user_ids,
                    title=f"Solicitud PR-{purchase_id} recibida",
                    body="Hay una nueva solicitud de compra pendiente de gestión.",
                )

                # Avisar creador
                self.push_service.send_to_user(
                    user_id=creator_id,
                    title="Solicitud aprobada",
                    body=f"Tu solicitud de compra PR-{purchase_id} ha sido aprobada por Gerencia.",
                )

                if creator_level_id != self.leader_lvl:
                    leader, lc = self.user_repository.get_leader(creator_department_id)
                    if lc != 200:
                        return leader, lc
                    
                    # Avisar leader
                    self.push_service.send_to_user(
                        user_id=leader.id,
                        title="Solicitud aprobada",
                        body=f"La solicitud de compra PR-{purchase_id} ha sido aprobada por Gerencia.",
                    )
            
            elif level_id in [self.leader_lvl, self.admin_lvl]:
                if express == 1:
                    if department_id != self.purchases_dep:
                        # Avisar area de compras
                        self.push_service.send_to_users(
                            user_ids=department_user_ids,
                            title=f"Solicitud PR-{purchase_id} recibida",
                            body="Hay una nueva solicitud de compra pendiente de gestión.",
                        )

                    # Avisar creador
                    self.push_service.send_to_user(
                        user_id=creator_id,
                        title="Solicitud aprobada",
                        body=f"Tu solicitud de compra PR-{purchase_id} ha sido aprobada.",
                    )
                else:
                    # Avisar creador
                    self.push_service.send_to_user(
                        user_id=creator_id,
                        title="Solicitud aprobada",
                        body=f"{format_name(user_name, True)} aprobó tu solicitud PR-{purchase_id}. En espera de Gerencia.",
                    )

                    manager, lc = self.user_repository.get_manager()
                    if lc != 200:
                        return manager, lc
                    
                    # Avisar manager
                    self.push_service.send_to_user(
                        user_id=manager.id,
                        title="Aprobación pendiente",
                        body=f"La solicitud de compra PR-{purchase_id} de {format_name(creator_name, True)} necesita tu aprobación.",
                    )

        else:
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
        
        level_id = user.level_id
        department_id = user.department_id

        if department_id in [8, 7] or user_id in [1, 23]:
            return self._get_manager_request_list(user_id)
        
        if level_id == self.leader_lvl:
            return self._get_leader_request_list(user_id, department_id)
        
        return self._get_worker_request_list(user_id)


    @handle_exceptions
    def _get_worker_request_list(self, user_id):
        purchase_requests, prc = self.purchase_repository.get_purchase_requests([user_id])
        if prc != 200:
            return purchase_requests, prc
        
        return self._format_requests_reponse(purchase_requests, user_id, self.worker_lvl)


    @handle_exceptions
    def _get_leader_request_list(self, user_id, department_id=None):
        department_user_ids, duic = self.user_repository.get_user_ids_by_department(department_id)
        if duic != 200:
            return department_user_ids, duic
    
        purchase_requests, prc = self.purchase_repository.get_purchase_requests(department_user_ids)
        if prc != 200:
            return purchase_requests, prc
        
        return self._format_requests_reponse(purchase_requests, user_id, self.leader_lvl)

    
    @handle_exceptions
    def _get_manager_request_list(self, user_id):
        purchase_requests, prc = self.purchase_repository.get_purchase_requests([])
        if prc != 200:
            return purchase_requests, prc
        
        return self._format_requests_reponse(purchase_requests, user_id, self.leader_lvl)
    

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

        current_user_id = int(get_jwt_identity())
        user, uc = self.user_repository.get_user_by_id(current_user_id)
        if uc != 200:
            return user, uc
        
        user_name = user.name
        purchase, pc = self.purchase_repository.get_purchase_by_id(data["purchase_id"])
        if pc != 200:
            return purchase, pc

        purchase_id =purchase.id

        chat, cc = self.purchase_repository.add_chat(
            purchase_id=purchase_id,
            user_id=current_user_id,
            comment=comment
        )
        if cc != 200:
            return chat, cc

        participants, _ = self.purchase_repository.get_chat_participants(
            purchase_id=purchase_id,
            exclude_user_id=current_user_id,
            include_owner=True,
        )
        
        self.push_service.send_to_users(
            user_ids=participants,
            title=f"Nuevo mensaje, solicitud PR-{purchase_id}",
            body=f"{format_name(user_name, True)}: {comment}",
        )
        socketio.emit("purchase_update_dashboard", {})

        return {
            "id": chat.id,
            "comment": chat.comment,
            "commenter_id": chat.commenter_id,
            "commenter_name": format_name(chat.commenter.name),
            "commenter_image": chat.commenter.image,
            "created_at": format_datetime(chat.created_at),
        }, 200