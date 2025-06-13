import logging
import threading
import base64
import uuid
import re
import unicodedata
from weasyprint import HTML
from flask import render_template, make_response
from datetime import datetime, timezone, timedelta
from application.handlers import handle_exceptions
from application.repository.support_repository import SupportRepository
from application.repository.machine_repository import MachineRepository
from application.repository.user_repository import UserRepository
from application.repository.general_repository import GeneralRepository
from application.services.general_service import GeneralService
from application.repository.client_repository import ClientRepository
from application.proxy.whatsapp import Whatsapp
from application import socketio
from config import Config


class SupportService:
    def __init__(self):
        self.support_repository = SupportRepository()
        self.machine_repository = MachineRepository()
        self.user_repository = UserRepository()
        self.general_repository = GeneralRepository()
        self.general_service = GeneralService()
        self.client_repository = ClientRepository()
        self.whatsapp = Whatsapp()
        self.days = {
            1: "lunes", 2: "martes", 3: "miércoles", 4: "jueves",
            5: "viernes", 6: "sábado", 7: "domingo"
        }
        self.months = {
            1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
            5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
            9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
        }


    def date_format(self, fecha):
        dia_semana = self.days[fecha.isoweekday()]
        dia = fecha.day
        mes = self.months[fecha.month]

        return f"{dia} de {mes} del {fecha.year}"


    @handle_exceptions
    def calculate_passed_days(self, start_date):
        holidays = [
            "2023-12-25", "2024-01-01", "2024-03-28", "2024-03-29",
            "2024-05-01", "2024-06-07", "2024-06-29", "2024-07-23",
            "2024-07-28", "2024-07-29", "2024-08-06", "2024-08-30",
            "2024-10-08", "2024-11-01", "2024-12-08", "2024-12-09",
            "2024-12-25"
        ]
        
        tday = (datetime.today() - timedelta(hours=5)).date()
        current = start_date.date() if isinstance(start_date, datetime) else start_date
        passed_days = 0

        while current < tday:
            if current.weekday() < 5 and current.strftime('%Y-%m-%d') not in holidays:
                passed_days += 1
            current += timedelta(days=1)
        
        return passed_days


    @handle_exceptions
    def order_consult(self, order_number, document):
        service_order, service_order_status = self.support_repository.get_service_order_by_number_and_document(order_number, document) 
        if service_order_status != 200:
            return service_order, service_order_status
        
        register_days = self.calculate_passed_days(service_order.register_at)

        order_data = {
            "order_number": f"{service_order.order_number}",
            "technician_name": self.general_service.format_name(service_order.technician.name),
            "machine": f"{service_order.machine.brand.name} {service_order.machine.model}",
            "machine_image": service_order.machine.image,
            "client_name": service_order.client.name.title(),
            "client_email": service_order.client.email,
            "status_text": f"Estado actual de la orden: <b>{service_order.status.name}</b>",
            "status_id": service_order.status_id,
            "origin_name": service_order.origin.name,
            "method_name": service_order.method.name,
            "passed_days": f"{register_days} " + ("días" if register_days > 1 else "día")
        }

        history, history_status = self.support_repository.get_service_order_history(service_order.id) 
        if history_status != 200:
            return history, history_status
        
        service_status, service_order_status = self.general_repository.get_service_status() 
        if service_order_status != 200:
            return service_status, service_order_status
        
        
        history_dict = [
            {
                "status_name": row.status.name,
                # "user_name": row.user.name.split()[0],
                # "notes": row.notes if row.notes else "",
                "register_at": f"{row.register_at.day} de {self.months[row.register_at.month]} de {row.register_at.year}"
            } for row in history
        ]

        order_data["history"] = history_dict

        return order_data, 200
    

    @handle_exceptions
    def service_order_next(self, order_number, user_id, notes, send):
        service_order, service_order_status = self.support_repository.get_service_order_by_number(order_number) 
        if service_order_status != 200:
            return service_order, service_order_status

        utc_now = datetime.now(timezone.utc)
        stamp = utc_now - timedelta(hours=5)
        current_status_id = service_order.status_id
        service_order_id = service_order.id
        client_name = service_order.client.name
        client_phone = service_order.client.phone
        machine_id = service_order.machine_id

        next_order, next_order_status = self.support_repository.next_service_order(service_order, current_status_id, stamp) 
        if next_order_status != 200:
            return next_order, next_order_status
        
        new_order_status, new_order_status_code = self.support_repository.new_order_status(service_order_id, current_status_id, user_id, stamp, notes) 
        if new_order_status_code != 200:
            return new_order_status, new_order_status_code
        
        socketio.emit("support_dashboard_update", {})
        
        machine, machine_status = self.machine_repository.get_machine(machine_id)
        if machine_status != 200:
            return machine, machine_status
        
        machine_name = machine.full_name
        if send:
            threading.Thread(target=self.whatsapp.status_change, args=(current_status_id, client_phone, client_name, machine_name)).start()
        return "Order de servicio actualizada correctamente", 200
    

    @handle_exceptions
    def service_order_prev(self, order_number, user_id):
        service_order, service_order_status = self.support_repository.get_service_order_by_number(order_number) 
        if service_order_status != 200:
            return service_order, service_order_status
        
        current_status_id = service_order.status_id
        service_order_id = service_order.id
        order_status, order_status_code = self.support_repository.get_order_status(service_order_id, current_status_id) 
        if order_status_code != 200:
            return order_status, order_status_code
        
        delete_order, delete_order_code = self.support_repository.delete_order_status(order_status) 
        if delete_order_code != 200:
            return delete_order, delete_order_code

        previous_status, previous_status_code = self.support_repository.get_order_status(service_order_id, current_status_id - 1) 
        if previous_status_code != 200:
            return previous_status, previous_status_code
        
        previous_status_date = previous_status.register_at
        prev_order, prev_order_status = self.support_repository.prev_service_order(service_order, current_status_id, previous_status_date) 
        if prev_order_status != 200:
            return prev_order, prev_order_status
        
        return "Order de servicio actualizada correctamente", 200


    @handle_exceptions
    def format_date_to_string(self, date):
        date_obj = datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S")

        months = {
            1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
            5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
            9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
        }
        return f"{date_obj.day} de {months[date_obj.month]} de {date_obj.year}"


    @handle_exceptions
    def get_service_order_by_number(self, order_number):
        service_order, service_order_status = self.support_repository.get_service_order_by_number(order_number) 
        if service_order_status != 200:
            return service_order, service_order_status
        
        register_days = self.calculate_passed_days(service_order.register_at)
        
        order_data = {
            "order_number": service_order.order_number,
            "technician_id": service_order.technician_id,
            "technician_name": service_order.technician.name.split()[0],
            "machine": f"{service_order.machine.brand.name} {service_order.machine.model}",
            "machine_image": service_order.machine.image,
            "client_name": service_order.client.name.title(),
            "client_document": service_order.client.document,
            #"client_email": service_order.client.email,
            "client_phone": service_order.client.phone,
            "status_id": service_order.status_id,
            "origin_name": service_order.origin.name if service_order.origin else None,
            "origin_id": service_order.origin_id,
            "method_name": service_order.method.name if service_order.method else None,
            "method_id": service_order.method_id,
            "paid": service_order.paid,
            "pay_amount": service_order.pay_amount,
            "priority": self.get_priority(service_order.status_id, register_days),
            #"status_text": f"Estado actual de la orden: {service_order.status.name}",
            "passed_days": f"{register_days} " + ("días" if register_days > 1 else "día")
        }

        history, history_status = self.support_repository.get_service_order_history(service_order.id) 
        if history_status != 200:
            return history, history_status
        
        service_status, service_order_status = self.general_repository.get_service_status() 
        if service_order_status != 200:
            return service_status, service_order_status
        
        history_dict = [
            {
                "status_id": row.status_id,
                "user_name": row.user.name.split()[0],
                "notes": row.notes if row.notes else "",
                #"register_at": self.format_date_to_string(row.register_at),
                "register_at":  row.register_at.strftime("%d-%m-%y")

            } for row in history
        ]

        order_data["history"] = history_dict

        return order_data, 200
    

    @handle_exceptions
    def get_priority(self, status_id, passed_days):
        if status_id < 5:
            if passed_days < 4:
                return "low"
            if passed_days < 8:
                return "mid"
            return "high"
        
        if passed_days < 14:
            return "low"
        if passed_days < 18:
            return "mid"
        return "high"


    @handle_exceptions
    def support_dashboard(self, user_id):
        leader = self.user_repository.get_support_leader()
        user, user_status = self.user_repository.get_user_by_id(user_id)
        if user_status != 200:
            return user, user_status
        
        service_orders, service_order_status = self.support_repository.get_working_service_order(leader, user) 
        if service_order_status != 200:
            return service_orders, service_order_status

        service_status, service_order_status = self.general_repository.get_service_status() 
        if service_order_status != 200:
            return service_status, service_order_status
        
        result = []
        for status in service_status:
            status_order = [service_order for service_order in service_orders if service_order.status_id == status.id]
            
            status_orders = []
            for order in status_order:
                register_days = self.calculate_passed_days(order.register_at)
                #updated_days = self.calculate_passed_days(order.updated_at)

                technician_name = order.technician.name.split()[0] if order.technician and order.technician.name else None

                service_order_data = {
                    "order_number": order.order_number,
                    "technician_name": technician_name,
                    "machine": order.machine.model,
                    "machine_image": order.machine.image,
                    "method_name": order.method.name if order.method else None,
                    "method_letter": order.method.name[0] if order.method and order.method.name else None,
                    "paid": order.paid,
                    "priority": self.get_priority(order.status_id, register_days),
                    "register_days_int": register_days,
                    "register_days": f"{register_days} d.",
                    #"updated_days": updated_days,
                    "status_id": status.id,
                }
                    
                status_orders.append(service_order_data)
            
            status_orders.sort(key=lambda x: x["register_days_int"], reverse=True)

            result.append({
                "status_id": status.id,
                "status_name": status.name,
                "service_order": status_orders
            })
        return result, 200
        

    @handle_exceptions
    def ready_list(self):
        service_orders, service_order_status = self.support_repository.get_ready_service_order() 
        if service_order_status != 200:
            return service_orders, service_order_status

        list = []
        for order in service_orders:
            register_days = self.calculate_passed_days(order.register_at)

            technician_name = order.technician.name.split()[0] if order.technician and order.technician.name else None

            service_order_data = {
                "service_order_id": order.id,
                "order_number": order.order_number,
                "client_name": order.client.name,
                "client_phone": order.client.phone[2:],
                "technician_name": technician_name,
                "machine": order.machine.model,
                "machine_image": order.machine.image,
                "method_name": order.method.name if order.method else None,
                "method_letter": order.method.name[0] if order.method and order.method.name else None,
                "paid": order.paid,
                "priority": self.get_priority(order.status_id, register_days),
                "register_days_int": register_days,
                "register_days": f"{register_days} d.",
                #"updated_days": updated_days,
                "status_id": order.status_id,
            }
                
            list.append(service_order_data)
        
        list.sort(key=lambda x: x["register_days_int"], reverse=True)

        return list, 200
    

    @handle_exceptions
    def service_order_new(self, data):
        data["status_id"] = 1
        machine_id = data.get("machine_id")
        token = data.get("token")
        user_id = data.get("user_id")
        notes = data.get("notes").strip()
        register_at = data.get("register_at")

        client_id = data.get("client_id")
        client_data = data.pop("client")

        document = client_data.get("document", "").strip()
        name = client_data.get("name", "").strip()
        phone = client_data.get("phone", "").strip()
        is_from_bot = int(user_id) == 21

        if not machine_id:
            return "Selecciona un equipo", 400
        if is_from_bot and not notes:
            return "Describe el problema", 400
        if not is_from_bot:
            if not register_at:
                return "Selecciona la fecha de ingreso", 400
        else:
            utc_now = datetime.now(timezone.utc)
            peru_time = utc_now - timedelta(hours=5)
            data["register_at"] = peru_time

        if client_id:
            client, client_status = self.client_repository.get_client_by_id(client_id)
            if client_status != 200:
                return client, client_status
            self.client_repository.update_client(client, client_data)
        else:
            if not document:
                return "Ingrese un documento", 400
            if not name:
                return "Ingrese el nombre", 400
            if not phone or len(phone) != 9:
                return "Ingresa un celular válido", 400
            
            client, client_status = self.client_repository.get_client_by_document(document)
            if client_status == 500:
                return client, client_status
            if client_status == 404:
                added_client, added_client_status = self.client_repository.add_client(client_data)
                if added_client_status != 200:
                    return added_client, added_client_status
                data["client_id"] = added_client
            else:

                data["client_id"] = client.id
        
        order_number = self.support_repository.get_next_order_number()
        leader = self.user_repository.get_support_leader()

        signature_data = data.get('signature')
        if signature_data:
            header, encoded = signature_data.split(",", 1)
            binary_data = base64.b64decode(encoded)
            filename = f"signature_{uuid.uuid4().hex}.png"

            with open(f"/shared_uploads/client_signatures/{filename}", "wb") as f:
                f.write(binary_data)

            data['signature'] = filename
            logging.info(f"Firma guardada como: {filename}")

        service_order_id, service_order_status = self.support_repository.new_service_order(
            order_number,
            leader.id,
            data
        )
        if service_order_status != 200:
            return service_order_id, service_order_status
        
        socketio.emit("support_dashboard_update", {})
        order_status, service_status = self.support_repository.add_order_status(service_order_id, user_id, data)
        if service_status != 200:
            return order_status, service_status
        
        machine, machine_status = self.machine_repository.get_machine(machine_id)
        if machine_status != 200:
            return machine, machine_status
        
        if not phone.startswith("51"):
            phone = f"51{phone}"
            
        machine_name = machine.full_name
        threading.Thread(target=self.whatsapp.new_order, args=(phone, notes, order_number, machine_name)).start()
        if is_from_bot and leader.phone:
            threading.Thread(target=self.whatsapp.new_order_alert, args=(leader.phone, order_number, machine_name)).start()

        return "Orden registrada correctamente", 200


    @handle_exceptions
    def service_link_order_new(self, data):
        token = data.get("token")
        link, link_status = self.support_repository.get_link_by_token(token) 
        if link_status != 200:
            return link, link_status
        
        if link.status_id >= 3:
            return "Link inválido", 400
        
        data["status_id"] = 1
        data["method_id"] = 3
        machine_id = data.get("machine_id")
        notes = data.get("notes").strip()
        client_data = data.pop("client")

        document = client_data.get("document", "").strip()
        name = client_data.get("name", "").strip()
        phone = client_data.get("phone", "").strip()
        utc_now = datetime.now(timezone.utc)
        peru_time = utc_now - timedelta(hours=5)
        data["register_at"] = peru_time

        if not machine_id:
            return "Selecciona un equipo", 400
        if not notes:
            return "Describe el problema", 400
        if not document:
            return "Ingrese un documento", 400
        
        client, client_status = self.client_repository.get_client_by_document(document)
        if client_status == 500:
            return client, client_status
        
        if client_status == 200:
            data["client_id"] = client.id
            self.client_repository.update_client(client, client_data)
        else:
            if not name:
                return "Ingrese el nombre", 400
            if not phone or len(phone) != 9:
                return "Ingresa un celular válido", 400
            
            added_client, added_client_status = self.client_repository.add_client(client_data)
            if added_client_status != 200:
                return added_client, added_client_status
            data["client_id"] = added_client
        
        order_number = self.support_repository.get_next_order_number()
        leader = self.user_repository.get_support_leader()

        signature_data = data.get('signature')
        if signature_data:
            header, encoded = signature_data.split(",", 1)
            binary_data = base64.b64decode(encoded)
            filename = f"signature_{uuid.uuid4().hex}.png"

            with open(f"/shared_uploads/client_signatures/{filename}", "wb") as f:
                f.write(binary_data)

            data['signature'] = filename
            logging.info(f"Firma guardada como: {filename}")

        service_order_id, service_order_status = self.support_repository.new_service_order(
            order_number,
            leader.id,
            data
        )
        if service_order_status != 200:
            return service_order_id, service_order_status
        
        socketio.emit("support_dashboard_update", {})
        order_status, service_status = self.support_repository.add_order_status(service_order_id, 21, data)
        if service_status != 200:
            return order_status, service_status
        
        machine, machine_status = self.machine_repository.get_machine(machine_id)
        if machine_status != 200:
            return machine, machine_status
        
        if not phone.startswith("51"):
            phone = f"51{phone}"
            
        machine_name = machine.full_name
        threading.Thread(target=self.whatsapp.new_order, args=(phone, notes, order_number, machine_name)).start()
        if leader.phone:
            threading.Thread(target=self.whatsapp.new_order_alert, args=(leader.phone, order_number, machine_name)).start()

        update_link, update_link_status = self.support_repository.update_link_client(link, order_number, data["client_id"]) 
        if update_link_status != 200:
            return update_link, update_link_status
        
        socketio.emit("support_link_update", {})
        return {"order_number": order_number}, 200
    

    @handle_exceptions
    def service_order_update(self, data):
        order_number = data.get("order_number")
        user_id = data.get("user_id")

        service_order, service_order_status = self.support_repository.get_service_order_by_number(order_number) 
        if service_order_status != 200:
            return service_order, service_order_status

        update_order, update_order_status = self.support_repository.update_service_order(service_order, data) 
        if update_order_status != 200:
            return update_order, update_order_status
        
        socketio.emit("support_dashboard_update", {})

        return "Order de servicio actualizada correctamente", 200


    @handle_exceptions
    def history(self, data):
        page = data.get("page")
        per_page = data.get("per_page")
        service_orders, service_orders_status = self.support_repository.get_all_service_orders(page=page, per_page=per_page)
        if service_orders_status != 200:
            return service_orders, service_orders_status
        
        list = []
        for order in service_orders["list"]:
            order_data = {
                "id": order.id,
                "order_number": order.order_number,
                "client_name": order.client.name.title(),
                #"technician_name": order.technician.name.title(),
                "method_name": order.method.name,
                "method_letter": order.method.name[0] if order.method.name else None,
                "origin_name": order.origin.name,
                "finished": False if order.status_id < 9 else True,
                "machine": order.machine.model,
                "brand": order.machine.brand.name,
                "machine_image": order.machine.image,
                "register_at": self.date_format(order.register_at)
            }
            list.append(order_data)

        return {
            "list": list,
            "pagination": {
                "total": service_orders["total"],
                "page": service_orders["page"],
                "per_page": service_orders["per_page"],
                "pages": service_orders["pages"],
            }
        }, 200
    

    @handle_exceptions
    def service_by_id(self, service_order_id):
        return self.support_repository.get_service_by_id(service_order_id)


    @handle_exceptions
    def finish(self, service_order, data):
        #order_number = data.get("order_number")
        user_id = data.get("user_id")
        filename = data.get("filename")

        utc_now = datetime.now(timezone.utc)
        stamp = utc_now - timedelta(hours=5)
        current_status_id = service_order.status_id
        service_order_id = service_order.id
        client_name = service_order.client.name
        client_phone = service_order.client.phone
        machine_id = service_order.machine_id

        next_order, next_order_status = self.support_repository.next_service_order(service_order, current_status_id, stamp) 
        if next_order_status != 200:
            return next_order, next_order_status
        
        new_order_status, new_order_status_code = self.support_repository.new_order_status(service_order_id, current_status_id, user_id, stamp, filename) 
        if new_order_status_code != 200:
            return new_order_status, new_order_status_code
        
        socketio.emit("support_dashboard_update", {})
        
        machine, machine_status = self.machine_repository.get_machine(machine_id)
        if machine_status != 200:
            return machine, machine_status
        
        threading.Thread(target=self.whatsapp.status_change, args=(current_status_id, client_phone, client_name, machine.full_name, filename)).start()
        return "Order de servicio actualizada correctamente", 200


    @handle_exceptions
    def create_link(self, user_id):
        token = str(uuid.uuid4()) 

        create_link, create_link_status = self.support_repository.create_link(token) 
        if create_link_status != 200:
            return create_link, create_link_status
        
        socketio.emit("support_link_update", {})
        return {
            "url": f"{Config.EXTERNAL_REGISTER_URL}{token}"
        }, 200


    @handle_exceptions
    def link_delete(self, data):
        user_id = data.get("user_id")
        link_id = data.get("link_id")

        link, link_status = self.support_repository.get_link(link_id) 
        if link_status != 200:
            return link, link_status
        
        delete_link, delete_link_status = self.support_repository.delete_link(link) 
        if delete_link_status != 200:
            return delete_link, delete_link_status
        
        socketio.emit("support_link_update", {})
        return "Link eliminado correctamente" , 200
    

    @handle_exceptions
    def verify_token(self, token):
        link, link_status = self.support_repository.get_link_by_token(token) 
        if link_status != 200:
            return link, link_status
        
        if link.status_id >= 3:
            return "Link inválido", 422
        
        update_link, update_link_status = self.support_repository.update_link(link) 
        if update_link_status != 200:
            return update_link, update_link_status
        
        socketio.emit("support_link_update", {})
        return "Link validado correctamente" , 200
    

    @handle_exceptions
    def link_history(self, data):
        page = data.get("page")
        per_page = data.get("per_page")
        service_links, service_links_status = self.support_repository.get_service_links_history(page=page, per_page=per_page)
        if service_links_status != 200:
            return service_links, service_links_status
        
        list = []
        for link in service_links["list"]:
            link_data = {
                "id": link.id,
                "url": f"{Config.EXTERNAL_REGISTER_URL}{link.token}",
                "order_number": link.order_number if link.order_number else '-',
                "client_name": link.client.name if link.client_id else '-',
                "status": link.status.name,
                "status_id": link.status_id,
                "register_at": link.created_at.strftime('%d/%m/%y %I:%M %p').lower()
            }
            list.append(link_data)

        return {
            "list": list,
            "pagination": {
                "total": service_links["total"],
                "page": service_links["page"],
                "per_page": service_links["per_page"],
                "pages": service_links["pages"],
            }
        }, 200
    

    @handle_exceptions
    def slugify(self, value):
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub(r'[^a-zA-Z0-9]+', '_', value)
        return value.strip('_').lower()


    def create_pdf(self, order_number):
        service_order, service_order_status = self.support_repository.get_service_order_by_number(order_number) 
        if service_order_status != 200:
            return service_order, service_order_status
        
        html_out = render_template('order_report.html', order=service_order)

        pdf = HTML(string=html_out).write_pdf()
        client_slug = self.slugify(service_order.client.name)
        filename = f"reporte_orden_{order_number}_{client_slug}.pdf"

        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        return response
    

    @handle_exceptions
    def statistics(self):
        total_orders, total_orders_code = self.support_repository.get_total_orders() 
        if total_orders_code != 200:
            return total_orders, total_orders_code
        
        today_orders, today_orders_code = self.support_repository.get_today_total_orders() 
        if today_orders_code != 200:
            return today_orders, today_orders_code
        
        week_orders, week_orders_code = self.support_repository.get_week_total_orders() 
        if week_orders_code != 200:
            return week_orders, week_orders_code

        month_orders, month_orders_code = self.support_repository.get_month_total_orders() 
        if month_orders_code != 200:
            return month_orders, month_orders_code

        orders_by_status, orders_by_status_code = self.support_repository.get_orders_by_status() 
        if orders_by_status_code != 200:
            return orders_by_status, orders_by_status_code
        by_status = [
            {"status_id": sid, "status": name, "count": count}
            for sid, name, count in orders_by_status
        ]

        orders_by_month, orders_by_month_code = self.support_repository.get_orders_by_month() 
        if orders_by_month_code != 200:
            return orders_by_month, orders_by_month_code
        by_month = [
            {'period': period, 'count': count}
            for period, count in orders_by_month
        ]
        
        orders_by_tech, orders_by_tech_code = self.support_repository.get_orders_by_tech() 
        if orders_by_tech_code != 200:
            return orders_by_tech, orders_by_tech_code
        by_tech = [
            {'technician': self.general_service.format_name(name), 'count': count}
            for name, count in orders_by_tech
        ]
        result = {
            "count":  {
                "total": total_orders or 0,
                "today": today_orders or 0,
                "week": week_orders or 0,
                "month": month_orders or 0
            },
            "by_status": by_status,
            "by_month": by_month,
            "by_tech": by_tech,
        }
        return result, 200
    

    @handle_exceptions
    def find_orders(self, order_number):
        if len(order_number) < 2:
            return None, 400
        
        orders, orders_status = self.support_repository.get_orders_like(order_number)
        if orders_status != 200:
            return orders, orders_status
        
        orders_list = [
            {
                "id": order.id,
                "order_number": order.order_number,
                "machine": order.machine.model,
                "client_name": order.client.name.title(),
                "machine_image": order.machine.image,

            } for order in orders
        ]
        return orders_list, 200