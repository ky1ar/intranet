import logging
from application.handlers import handle_exceptions
from application.utils import format_name, format_datetime
from application.services.push_service import PushSender
from application.services.module_service import ModuleService
from application.repository.purchase_repository import PurchaseRepository
from application.repository.user_repository import UserRepository
from application import socketio
from flask_jwt_extended import get_jwt_identity


_PMONTHS = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic",
}


class PurchaseService:
    def __init__(self):
        self.purchase_repository = PurchaseRepository()
        self.user_repository = UserRepository()
        self.push_service = PushSender()
        self.module_service = ModuleService()
        self.management_dep = 7
        self.purchases_dep = 8
        self.worker_lvl = 2
        self.leader_lvl = 3
        self.admin_lvl = 4


    def _has_perm(self, user_id, perm_slug):
        result, code = self.module_service.check_permission(user_id, 'purchases', perm_slug)
        if code != 200:
            return False
        return result.get('granted', False) if isinstance(result, dict) else False


    def _notify_managers(self, purchase_id):
        """Notifica a todos los usuarios con permiso 'manage'"""
        # Opción pragmática: buscar usuarios del dept compras + user_id 1
        # Opción ideal: query users con permiso manage en module purchases
        user_ids, duic = self.user_repository.get_user_ids_by_department(department_id=8)
        if duic == 200:
            user_ids.append(1)
            self.push_service.send_to_users(
                user_ids=list(set(user_ids)),
                title=f"Solicitud PR-{purchase_id} recibida",
                body="Hay una nueva solicitud de compra pendiente de gestión.",
            )

    def _notify_approvers_area(self, purchase_id, creator_user):
        """Notifica al líder del área del creador"""
        leader, lc = self.user_repository.get_leader(creator_user.department_id)
        if lc == 200:
            self.push_service.send_to_user(
                user_id=leader.id,
                title="Aprobación pendiente",
                body=f"La solicitud PR-{purchase_id} de {format_name(creator_user.name, True)} necesita tu aprobación.",
            )

    def _notify_approvers_manager(self, purchase_id, user_name):
        """Notifica a gerencia"""
        manager, mc = self.user_repository.get_manager()
        if mc == 200:
            self.push_service.send_to_user(
                user_id=manager.id,
                title="Aprobación pendiente",
                body=f"La solicitud PR-{purchase_id} de {format_name(user_name, True)} necesita tu aprobación.",
            )

    def _notify_owner(self, owner_id, purchase_id, message):
        """Notifica al creador de la solicitud"""
        self.push_service.send_to_user(
            user_id=owner_id,
            title=f"Solicitud PR-{purchase_id}",
            body=message,
        )
        

    @handle_exceptions
    def process(self, data):
        user_id = int(get_jwt_identity())
        user, uc = self.user_repository.get_user_by_id(user_id)
        if uc != 200:
            return user, uc

        can_approve_area = self._has_perm(user_id, 'approve_area')
        can_approve_manager = self._has_perm(user_id, 'approve_manager')
        can_manage = self._has_perm(user_id, 'manage')
        express = data.get("express")

        # Determinar status inicial
        if can_approve_manager:
            # Gerencia: ya pasa a "aprobado por gerencia"
            initial_status = 3
        elif can_approve_area:
            # Líder de área: ya pasa a "aprobado por área"
            initial_status = 2
        else:
            # Worker: queda pendiente
            initial_status = 1

        data["_initial_status"] = initial_status

        new_purchase_id, aec = self.purchase_repository.add_purchase(data, user)
        if aec != 200:
            return new_purchase_id, aec

        socketio.emit("purchase_update_dashboard", {})

        # Notificaciones según status y flujo
        if initial_status == 3:
            # Gerencia aprobó directo → avisar a compras (manage)
            self._notify_managers(new_purchase_id)

        elif initial_status == 2:
            if express:
                # Express + aprobado por área → salta gerencia → avisar compras
                self._notify_managers(new_purchase_id)
                self._notify_owner(user_id, new_purchase_id, "Tu solicitud express fue aprobada.")
            else:
                # Estándar → avisar gerencia
                self._notify_approvers_manager(new_purchase_id, user.name)

        elif initial_status == 1:
            # Worker → avisar líder de área
            self._notify_approvers_area(new_purchase_id, user)

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

        status_id = purchase.status_id
        is_owner = (user_id == purchase.user_id)

        can_approve_area = self._has_perm(user_id, 'approve_area')
        can_approve_manager = self._has_perm(user_id, 'approve_manager')
        can_manage = self._has_perm(user_id, 'manage')

        # Determinar modal
        if status_id == 1:
            if is_owner:
                modal = "edit"
            elif can_approve_area:
                modal = "approve"
            elif can_approve_manager:
                modal = "approve"
            else:
                modal = "view"

        elif status_id == 2:
            if can_approve_manager:
                modal = "approve"
            elif can_manage:
                modal = "delete"   # compras puede eliminar en status 2
            elif is_owner or can_approve_area:
                modal = "delete"
            else:
                modal = "view"
        else:
            modal = "view"

        dto = {
            "modal": modal,
            "id": purchase.id,
            "pr": f"PR-{purchase.id}",
            "type_id": purchase.type_id,
            "type_name": purchase.purchase_type.name,
            "urgency_id": purchase.urgency_id,
            "urgency_name": purchase.purchase_urgency.name,
            "express": bool(purchase.express),
            "it_validation": bool(purchase.it_validation),
            "needed_date": purchase.needed_date.isoformat() if purchase.needed_date else None,
            "status_name": purchase.status.name,
            "status_slug": purchase.status.slug,
            "status_id": status_id,
            "self_created": is_owner,

            "user_name": format_name(purchase.user.name),
            "created_at": format_datetime(purchase.created_at),

            # Flags de permisos para el frontend
            "can_approve_area": can_approve_area,
            "can_approve_manager": can_approve_manager,
            "can_manage": can_manage,

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

            can_approve_area = self._has_perm(user_id, 'approve_area')
            can_approve_manager = self._has_perm(user_id, 'approve_manager')

            purchase, pc = self.purchase_repository.get_purchase_by_id(purchase_id)
            if pc != 200:
                return purchase, pc

            express = purchase.express
            creator_id = purchase.user_id

            if can_approve_manager:
                # Gerencia aprueba → status 3 → avisar compras
                status, sc = self.purchase_repository.set_status(purchase_id, 3)
                if sc != 200:
                    return status, sc

                self._notify_managers(purchase_id)
                self._notify_owner(creator_id, purchase_id, 
                    f"Tu solicitud PR-{purchase_id} ha sido aprobada por Gerencia.")

            elif can_approve_area:
                if express:
                    # Express → salta gerencia → status 3 → avisar compras
                    status, sc = self.purchase_repository.set_status(purchase_id, 3)
                    if sc != 200:
                        return status, sc
                    self._notify_managers(purchase_id)
                else:
                    # Estándar → status 2 → avisar gerencia
                    status, sc = self.purchase_repository.set_status(purchase_id, 2)
                    if sc != 200:
                        return status, sc
                    self._notify_approvers_manager(purchase_id, user.name)

                self._notify_owner(creator_id, purchase_id,
                    f"Tu solicitud PR-{purchase_id} ha sido aprobada.")
            else:
                return "No autorizado para aprobar", 403

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

        can_view_all = self._has_perm(user_id, 'view_all')

        if can_view_all:
            # Ve TODAS las solicitudes
            purchase_requests, prc = self.purchase_repository.get_purchase_requests([])
            if prc != 200:
                return purchase_requests, prc
            return self._format_requests_reponse(purchase_requests, user_id)

        # Construir lista de user_ids visibles según permisos view_*
        visible_user_ids = set()
        visible_user_ids.add(user_id)  # siempre ve las propias

        # Obtener permisos del usuario para el módulo purchases
        modules_data, _ = self.module_service.get_user_modules(user_id)
        purchases_perms = {}
        if isinstance(modules_data, list):
            for m in modules_data:
                if m['slug'] == 'purchases':
                    purchases_perms = m.get('permissions', {})
                    break

        # Buscar permisos view_* activos
        department_slugs = []
        for perm_slug, granted in purchases_perms.items():
            if granted and perm_slug.startswith('view_'):
                dept_slug = perm_slug.replace('view_', '')
                department_slugs.append(dept_slug)

        if department_slugs:
            # Obtener user_ids de esos departamentos
            area_user_ids, duic = self.user_repository.get_user_ids_by_department_slugs(department_slugs)
            if duic == 200:
                visible_user_ids.update(area_user_ids)

        purchase_requests, prc = self.purchase_repository.get_purchase_requests(list(visible_user_ids))
        if prc != 200:
            return purchase_requests, prc

        return self._format_requests_reponse(purchase_requests, user_id)


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
    def _format_requests_reponse(self, purchase_requests, user_id):
        statuses, sc = self.purchase_repository.get_statuses()
        if sc != 200:
            return statuses, sc

        by_status = {s.id: [] for s in statuses}
        # Tope (10) solo en la columna terminal "Entregado" (status_id=7), que acumula
        # cientos; las demás etapas se muestran completas.
        for purchase in purchase_requests:
            if purchase.status_id not in by_status:
                continue
            if purchase.status_id == 7 and len(by_status[purchase.status_id]) >= 10:
                continue
            by_status[purchase.status_id].append({
                "id": purchase.id,
                "pr": f"PR-{purchase.id:04d}",
                "requester_name": format_name(purchase.user.name) if user_id != purchase.user_id else 'Tú',
                "requester_department": purchase.user.department.name,
                "requester_image": purchase.user.image,
                "type_name": purchase.purchase_type.name,
                "urgency_name": purchase.purchase_urgency.name,
                "urgency_slug": purchase.purchase_urgency.slug,
                "express": purchase.express,
                "status_name": purchase.status.name,
                "status_slug": purchase.status.slug,
                "created_at": format_datetime(purchase.created_at),
            })

        return [
            {
                "status_id": s.id,
                "status_name": s.name,
                "status_slug": s.slug,
                "requests": by_status[s.id],
            }
            for s in statuses
        ], 200


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

    
    def _get_visibility(self, user_id):
        """Devuelve la lista de user_ids visibles para el usuario, o [] si ve todo."""
        if self._has_perm(user_id, 'view_all'):
            return []

        visible = {user_id}

        modules_data, _ = self.module_service.get_user_modules(user_id)
        purchases_perms = {}
        if isinstance(modules_data, list):
            for m in modules_data:
                if m['slug'] == 'purchases':
                    purchases_perms = m.get('permissions', {})
                    break

        department_slugs = [
            slug.replace('view_', '')
            for slug, granted in purchases_perms.items()
            if granted and slug.startswith('view_')
        ]

        if department_slugs:
            area_ids, code = self.user_repository.get_user_ids_by_department_slugs(department_slugs)
            if code == 200:
                visible.update(area_ids)

        return list(visible)


    @handle_exceptions
    def find(self, query):
        user_id = int(get_jwt_identity())
        visibility = self._get_visibility(user_id)

        results, code = self.purchase_repository.find_purchases(query, visibility)
        if code != 200:
            return results, code

        data = [
            {
                "id": p.id,
                "requester_name": format_name(p.user.name) if p.user_id != user_id else "Tú",
                "requester_department": p.user.department.name,
                "requester_image": p.user.image,
                "urgency_name": p.purchase_urgency.name,
                "urgency_slug": p.purchase_urgency.slug,
                "express": p.express,
                "status_name": p.status.name,
                "status_slug": p.status.slug,
                "created_at": format_datetime(p.created_at),
            }
            for p in results
        ]

        return data, 200


    @handle_exceptions
    def statistics(self):
        total, _          = self.purchase_repository.stats_total()
        pending, _        = self.purchase_repository.stats_pending()
        total_amount, _   = self.purchase_repository.stats_total_amount()
        month_amount, _   = self.purchase_repository.stats_total_amount(month_only=True)
        month_rows, _     = self.purchase_repository.stats_by_month()
        dept_rows, _      = self.purchase_repository.stats_by_department()
        amount_rows, _    = self.purchase_repository.stats_amount_by_department()

        by_month = [
            {"period": f"{_PMONTHS.get(int(p.split('-')[1]), p)} {p[:4]}", "count": c}
            for p, c in month_rows
        ]
        by_department = [
            {"department": (name or "Sin área"), "count": c}
            for name, c in dept_rows
        ]
        amount_by_department = [
            {"department": (name or "Sin área"), "amount": float(a or 0)}
            for name, a in amount_rows
        ]

        return {
            "count": {
                "total": total,
                "pending": pending,
                "total_amount": float(total_amount or 0),
                "month_amount": float(month_amount or 0),
            },
            "by_month": by_month,
            "by_department": by_department,
            "amount_by_department": amount_by_department,
        }, 200

    @handle_exceptions
    def history(self, page):
        user_id = int(get_jwt_identity())
        visibility = self._get_visibility(user_id)

        result, code = self.purchase_repository.get_purchase_history(visibility, page)
        if code != 200:
            return result, code

        purchases = result["list"]
        data = {
            "list": [
                {
                    "id": p.id,
                    "requester_name": format_name(p.user.name) if p.user_id != user_id else "Tú",
                    "requester_image": p.user.image,
                    "requester_department": p.user.department.name,
                    "urgency_name": p.purchase_urgency.name,
                    "urgency_slug": p.purchase_urgency.slug,
                    "express": p.express,
                    "status_name": "Eliminada" if p.deleted_at else p.status.name,
                    "status_slug": "deleted" if p.deleted_at else p.status.slug,
                    "created_at": format_datetime(p.created_at),
                }
                for p in purchases
            ],
            "pagination": {
                "page": page,
                "pages": result["pages"],
                "total": result["total"],
            },
        }

        return data, 200


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