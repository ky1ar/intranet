import logging
import threading
from datetime import datetime, timezone, timedelta
from application.handlers import handle_exceptions
from application.repository.support_repository import SupportRepository
from application.repository.machine_repository import MachineRepository
from application.repository.user_repository import UserRepository
from application.repository.general_repository import GeneralRepository
from application.proxy.whatsapp import Whatsapp
from application import socketio


class SupportService:
    def __init__(self):
        self.support_repository = SupportRepository()
        self.machine_repository = MachineRepository()
        self.user_repository = UserRepository()
        self.general_repository = GeneralRepository()
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
            "passed_days": f"{self.calculate_passed_days(service_order.register_at)} días"
        }
        return order_data, 200
    

    @handle_exceptions
    def service_order_next(self, order_number, admin_id, notes):
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
        
        new_order_status, new_order_status_code = self.support_repository.new_order_status(service_order_id, current_status_id, admin_id, stamp, notes) 
        if new_order_status_code != 200:
            return new_order_status, new_order_status_code
        
        socketio.emit("support_dashboard_update", {})
        
        #self.whatsapp.status_change(current_status_id, client_phone, client_name)
        #threading.Thread(target=self.whatsapp.status_change, args=(current_status_id, client_phone, client_name)).start()
        return "Order de servicio actualizada correctamente", 200
    

    @handle_exceptions
    def service_order_prev(self, order_number, admin_id):
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
        
        order_data = {
            "order_number": service_order.order_number,
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
            #"status_text": f"Estado actual de la orden: {service_order.status.name}",
            "passed_days": f"{self.calculate_passed_days(service_order.register_at)} días"
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
                "admin_name": row.admin.name.split()[0],
                "notes": row.notes,
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
        machine_id = data.get("machine_id")
        admin_id = data.get("admin_id")
        notes = data.get("notes").strip()
        client_id = data.get("client_id")

        client_data = data.pop("client")
        document = client_data.get("document", "").strip()
        name = client_data.get("name", "").strip()
        phone = client_data.get("phone", "").strip()

        if not machine_id:
            return "Selecciona un equipo", 400
        if not notes:
            return "Describe el problema", 400
        
        if client_id:
            client, client_status = self.general_repository.get_user_by_id(client_id)
            if client_status != 200:
                return client, client_status
            client_name = client.name
            self.general_repository.update_client(client, client_data)
        else:
            if not phone or len(phone) != 9:
                return "Ingresa un celular válido", 400
            if not name:
                return "Ingresa un nombre del cliente", 400
            
            client, client_status = self.general_repository.add_client(client_data)
            if client_status != 200:
                return client, client_status
            client_name = client.name
            client_id = client.id
        
        utc_now = datetime.now(timezone.utc)
        register_at = utc_now - timedelta(hours=5)
        order_number = self.support_repository.get_next_order_number()
        leader = self.user_repository.get_support_leader()

        payload = {
            "order_number": order_number,
            "register_at": register_at,
            "technician_id": leader.id,
            "machine_id": machine_id,
            "client_id": client_id,
            "admin_id": admin_id,
            "status_id": 1,
            "notes": notes,
            "phone": phone,
        }
        
        shipping_order_id, service_order_status = self.support_repository.new_service_order(payload)
        if service_order_status != 200:
            return shipping_order_id, service_order_status
        
        order_status, service_status = self.support_repository.add_order_status(shipping_order_id, payload)
        if service_status != 200:
            return order_status, service_status
        
        machine, machine_status = self.machine_repository.get_machine(machine_id)
        if machine_status != 200:
            return machine, machine_status
        
        machine_name = machine.full_name

        threading.Thread(target=self.whatsapp.new_order, args=(payload, client_name, machine_name)).start()
        threading.Thread(target=self.whatsapp.new_order_alert, args=("946887982", order_number, machine_name)).start()
        #self.whatsapp.new_order(payload, client_name, machine_name)
        #socketio.emit("update_schedule", {})
        return "Orden registrada correctamente", 200






























    
    @handle_exceptions
    def service_order_process(self, data):
        edit = data.get("edit")
        order_number = data.get("order_number", "").strip()
        machine_id = data.get("machine_id")
        method_id = data.get("method_id")
        technician_id = data.get("technician_id")
        origin_id = data.get("origin_id")
        status_id = data.get("status_id")
        register_at = data.get("register_at")
        paid = data.get("paid")

        if not order_number:
            return "Ingrese el número de orden", 400
        
        service_order, service_order_status = self.support_repository.get_service_order_by_number(order_number)
        if service_order_status == 500:
            return service_order, service_order_status
        """ if edit:
            if service_order_status != 200:
                return "Orden de pedido no encontrada para edición", 400
            
            if not method_id:
                return "Seleccione un tipo de envío", 400
            if not register_date:
                return "Ingrese la fecha de registro", 400
            if not address:
                return "Ingrese la dirección", 400
            if not district_id:
                return "Seleccione un distrito", 400

            updated_fields = {}
            if service_order.method_id != method_id:
                updated_fields["method_id"] = method_id
            if service_order.register_date != register_date:
                updated_fields["register_date"] = register_date

            if service_order.address != address:
                updated_fields["address"] = address
            if service_order.district_id != district_id:
                updated_fields["district_id"] = district_id
            if service_order.maps != request.get("maps"):
                updated_fields["maps"] = request.get("maps")
            if service_order.vendor_id != request.get("vendor_id"):
                updated_fields["vendor_id"] = request.get("vendor_id")
            if service_order.driver_id != request.get("driver_id"):
                updated_fields["driver_id"] = request.get("driver_id")

            if updated_fields:
                self.service.update_shipping_order_data(service_order, updated_fields)

            history, history_status = self.service.add_history(admin_id, service_order.id, HistoryType.UPDATED, data=updated_fields)
            if history_status != 200:
                return history, history_status
            
            socketio.emit("update_schedule", {})
            return "Orden actualizada correctamente", 200
        """
        if service_order_status == 200:
            return "Este número de orden ya ha sido registrado", 400
        if not machine_id:
            return "Seleccione un producto", 400
        if not method_id:
            return "Seleccione un tipo de servicio", 400
        if not register_at:
            return "Ingrese la fecha de ingreso", 400
        if not technician_id:
            return "Seleccione un técnico", 400
        
        client_id = data.get("client_id")
        client_data = data.pop("client")

        document = client_data.get("document", "").strip()
        email = client_data.get("email", "").strip()
        name = client_data.get("name", "").strip()
        phone = client_data.get("phone", "").strip()

        if not email:
            return "Ingrese el email", 400
        if not phone or len(phone) != 9:
            return "Ingrese un celular válido", 400
    
        if client_id:
            client, client_status = self.general_repository.get_user_by_id(client_id)
            if client_status != 200:
                return client, client_status
            self.general_repository.update_client(client, client_data)
        else:
            if not document:
                return "Ingrese el documento", 400
            if len(document) not in (8, 11):
                return "Ingrese un documento válido", 400
            if not name:
                return "Ingrese un documento válido", 400
            
            added_client, added_client_status = self.general_repository.add_client(client_data)
            if added_client_status != 200:
                return added_client, added_client_status
            client_id = added_client
        
        service_order_id, service_order_status = self.support_repository.add_service_order(data)
        if service_order_status != 200:
            return service_order_id, service_order_status
        
        order_status, service_status = self.support_repository.add_order_status(service_order_id, data)
        if service_status != 200:
            return order_status, service_status
        #socketio.emit("update_schedule", {})
        return "Orden registrada correctamente", 200
    