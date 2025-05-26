import logging
import threading
import base64
import uuid
from datetime import datetime, timezone, timedelta
from application.handlers import handle_exceptions
from application.repository.support_repository import SupportRepository
from application.repository.machine_repository import MachineRepository
from application.repository.user_repository import UserRepository
from application.repository.general_repository import GeneralRepository
from application.repository.client_repository import ClientRepository
from application.proxy.whatsapp import Whatsapp
from application import socketio


class SupportService:
    def __init__(self):
        self.support_repository = SupportRepository()
        self.machine_repository = MachineRepository()
        self.user_repository = UserRepository()
        self.general_repository = GeneralRepository()
        self.client_repository = ClientRepository()
        self.whatsapp = Whatsapp()


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
            "order_number": f"00{service_order.order_number}",
            "technician_name": service_order.technician.name.title(),
            "machine": f"{service_order.machine.brand.name} {service_order.machine.model}",
            "client_name": service_order.client.name.title(),
            "client_email": service_order.client.email,
            "status_text": f"Estado actual de la orden: {service_order.status.name}",
            "status_id": service_order.status_id,
            "origin_name": service_order.origin.name,
            "method_name": service_order.method.name,
            "passed_days": f"{register_days} " + ("días" if register_days > 1 else "día")
        }
        return order_data, 200
    

    @handle_exceptions
    def service_order_next(self, order_number, user_id, notes):
        service_order, service_order_status = self.support_repository.get_service_order_by_number(order_number) 
        if service_order_status != 200:
            return service_order, service_order_status

        utc_now = datetime.now(timezone.utc)
        stamp = utc_now - timedelta(hours=5)
        current_status_id = service_order.status_id
        service_order_id = service_order.id
        client_name = service_order.client.name
        client_phone = service_order.client.phone

        next_order, next_order_status = self.support_repository.next_service_order(service_order, current_status_id, stamp) 
        if next_order_status != 200:
            return next_order, next_order_status
        
        new_order_status, new_order_status_code = self.support_repository.new_order_status(service_order_id, current_status_id, user_id, stamp, notes) 
        if new_order_status_code != 200:
            return new_order_status, new_order_status_code
        
        socketio.emit("support_dashboard_update", {})
        
        #self.whatsapp.status_change(current_status_id, client_phone, client_name)
        #threading.Thread(target=self.whatsapp.status_change, args=(current_status_id, client_phone, client_name)).start()
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
    def support_dashboard(self):
        service_orders, service_order_status = self.support_repository.get_working_service_order() 
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
    def service_order_new(self, data):
        data["status_id"] = 1
        machine_id = data.get("machine_id")
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
                client_id = added_client
            else:
                client_id = client.id
        
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
        
        machine_name = machine.full_name
        #threading.Thread(target=self.whatsapp.new_order, args=(phone, notes, name, machine_name)).start()
        if is_from_bot:
            #threading.Thread(target=self.whatsapp.new_order_alert, args=("946887982", order_number, machine_name)).start()
            pass

        return "Orden registrada correctamente", 200


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

























