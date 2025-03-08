import logging, re

from application import bcrypt, socketio
from application.models import HistoryType, ShippingStatusList
from application.services import BaseService
from application.handlers import handle_logs_and_exceptions, validate_request
from flask_jwt_extended import create_access_token

class BaseController:
    def __init__(self):
        self.service = BaseService()     


    @handle_logs_and_exceptions
    def send_message(self, data):
        return self.service.send_message(data, template=3)


    @handle_logs_and_exceptions
    def user_get_by_document(self, document):
        if not document:
            return 'Missing document', 400
        
        return self.service.get_user(document)
    

    @handle_logs_and_exceptions
    def general_drivers(self):
        return self.service.get_drivers()
    

    @handle_logs_and_exceptions
    def general_vendors(self):
        return self.service.get_vendors()
    

    @handle_logs_and_exceptions
    def general_districts(self):
        return self.service.get_districts()
    
    @handle_logs_and_exceptions
    def general_shipping_types(self):
        return self.service.get_shipping_types()
    

    @handle_logs_and_exceptions
    def order_get_by_number(self, number):
        shipping_order, order_status = self.service.get_shipping_by_order_number(number)
        if order_status != 200:
            return shipping_order, order_status
        
        result = shipping_order.to_dict()
        result.update({
            "address": shipping_order.address.title(),
            "district_name": shipping_order.district.name,
            "driver_name": shipping_order.driver.name,
            "method_name": shipping_order.method.name,
            "method_background": shipping_order.method.background,
            "method_border": shipping_order.method.border,
            "register_date_format": shipping_order.register_date.strftime("%Y-%m-%d")
        })

        contacts = []
        for contact in shipping_order.contacts:
            contacts.append({
                "name": contact.client.name.title(),
                "document": contact.client.document,
                "email": contact.client.email,
                "phone": contact.client.phone[2:],
                "document_id": contact.client.id
            })
        
        result["contacts"] = contacts 

        shipping_dates, shipping_dates_status = self.service.get_shipping_dates(shipping_order.id, shipping_order.status_id)
        if shipping_dates_status != 200:
            return shipping_dates, shipping_dates_status
        
        if shipping_order.status_id == 4:
            result["on_the_way_date"] = shipping_dates.get("on_the_way_date")
            result["delivered_date"] = shipping_dates.get("delivered_date")
        elif shipping_order.status_id == 6:
            result["on_the_way_date"] = shipping_dates.get("on_the_way_date")
            result["not_delivered_date"] = shipping_dates.get("not_delivered_date")
        
        return result, 200
        

    @handle_logs_and_exceptions
    def order_get_pending(self):
        return self.service.get_orders_by_status(status_id=1)


    @handle_logs_and_exceptions
    def order_process(self, request):
        if validation_error := validate_request(
            request, 
            {"edit", "order_number", "method_id", "driver_id", "admin_id" ,"address" ,"district_id" ,"register_date", "comments"}
        ):
            return validation_error, 400

        order_number = request.get("order_number", "").strip()
        edit = request.get("edit")
        method_id = request.get("method_id")
        admin_id = request.get("admin_id")
        register_date = request.get("register_date")
        district_id = request.get("district_id")
        address = request.get("address", "").strip()

        if not order_number:
            return "Ingrese el número de orden", 400

        shipping, shipping_status = self.service.get_shipping_by_order_number(order_number)
        if shipping_status == 500:
            return shipping, shipping_status

        if edit:
            if shipping_status != 200:
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
            if shipping.method_id != method_id:
                updated_fields["method_id"] = method_id
            if shipping.register_date != register_date:
                updated_fields["register_date"] = register_date

            if shipping.address != address:
                updated_fields["address"] = address
            if shipping.district_id != district_id:
                updated_fields["district_id"] = district_id
            if shipping.maps != request.get("maps"):
                updated_fields["maps"] = request.get("maps")
            if shipping.vendor_id != request.get("vendor_id"):
                updated_fields["vendor_id"] = request.get("vendor_id")
            if shipping.driver_id != request.get("driver_id"):
                updated_fields["driver_id"] = request.get("driver_id")

            if updated_fields:
                self.service.update_shipping_order_data(shipping, updated_fields)

            history, history_status = self.service.add_history(admin_id, shipping.id, HistoryType.UPDATED, data=updated_fields)
            if history_status != 200:
                return history, history_status
            
            socketio.emit("update_schedule", {})
            return "Orden actualizada correctamente", 200
        
        if shipping_status == 200:
            return "Este número de orden ya ha sido registrado", 400
        
        if not method_id:
            return "Seleccione un tipo de envío", 400
        if not register_date:
            return "Ingrese la fecha de registro", 400
        if not address:
            return "Ingrese la dirección", 400
        if not district_id:
            return "Seleccione un distrito", 400
        
        client_id = request.get("client_id")
        client_data = request.pop("client")

        document = client_data.get("document", "").strip()
        email = client_data.get("email", "").strip()
        name = client_data.get("name", "").strip()
        phone = client_data.get("phone", "").strip()

        if not email:
            return "Ingrese el email", 400
        if not phone or len(phone) != 9:
            return "Ingrese un celular válido", 400
    
        if client_id:
            client, client_status = self.service.get_user_by_id(client_id)
            if client_status != 200:
                return client, client_status
            self.service.update_client(client, client_data)
        else:
            if not document:
                return "Ingrese el documento", 400
            if len(document) not in (8, 11):
                return "Ingrese un documento válido", 400
            if not name:
                return "Ingrese un documento válido", 400
            
            added_client, added_client_status = self.service.add_client(client_data)
            if added_client_status != 200:
                return added_client, added_client_status
            client_id = added_client
        
        shipping_order_id, shipping_order_status = self.service.add_shipping_order(request)
        if shipping_order_status != 200:
            return shipping_order_id, shipping_order_status

        shipping_contact, shipping_contact_status = self.service.add_shipping_contact(shipping_order_id, client_id)
        if shipping_contact_status != 200:
            return shipping_contact, shipping_contact_status
        
        history, history_status = self.service.add_history(admin_id, shipping_order_id, HistoryType.ADDED)
        if history_status != 200:
            return history, history_status
        
        socketio.emit("update_schedule", {})
        return "Orden registrada correctamente", 200


    @handle_logs_and_exceptions
    def photo_upload(self, request):
        if validation_error := validate_request(
            request, 
            {"order_number", "proof_photo"}
        ):
            return validation_error, 400

        order_number = request.pop("order_number")
        order, order_status = self.service.get_shipping_by_order_number(order_number)
        if order_status != 200:
            return order, order_status
        
        return self.service.update_shipping_order(order, request)


    @handle_logs_and_exceptions
    def order_set(self, request):
        if validation_error := validate_request(
            request, 
            {"order_number", "admin_id"}
        ):
            return validation_error, 400

        admin_id = request.get("admin_id")

        order_number = request.get("order_number")
        shipping_order, shipping_order_status = self.service.get_shipping_by_order_number(order_number)
        if shipping_order_status != 200:
            return shipping_order, shipping_order_status
        
        contact = shipping_order.contacts[0]
        status_id = request.get("status_id")
        if status_id == 3 or status_id == 4 or status_id == 6:
            data = {
                "phone": contact.client.phone,
                "username": contact.client.name.title(),
                "order_number": shipping_order.order_number,
                "schedule_id": shipping_order.schedule_id,
                "file": shipping_order.proof_photo
            }
            if shipping_order.method_id < 3:
                self.service.send_message(data, status_id)

        status = None
        if status_id == 1:
            status = ShippingStatusList.PENDING
        elif status_id == 2:
            status = ShippingStatusList.SCHEDULED
        elif status_id == 3:
            status = ShippingStatusList.ON_THE_WAY
        elif status_id == 4:
            status = ShippingStatusList.DELIVERED
        elif status_id == 6:
            status = ShippingStatusList.NOT_DELIVERED

        history, history_status = self.service.add_history(admin_id, shipping_order.id, HistoryType.STATUS_CHANGE, status, data=request)
        if history_status != 200:
            return history, history_status
        
        return self.service.update_shipping_order(shipping_order, request)


    @handle_logs_and_exceptions
    def order_delete(self, request):
        if validation_error := validate_request(
            request, 
            {"order_number", "admin_id"}
        ):
            return validation_error, 400

        admin_id = request.get("admin_id")
        order_number = request.get("order_number")
        shipping_order, shipping_order_status = self.service.get_shipping_by_order_number(order_number)
        if shipping_order_status != 200:
            return shipping_order, shipping_order_status
        
        history, history_status = self.service.add_history(admin_id, shipping_order.id, HistoryType.DELETED)
        if history_status != 200:
            return history, history_status
        
        return self.service.delete_shipping_order(shipping_order)
    

    @handle_logs_and_exceptions
    def order_schedule(self, offset=0):
        return self.service.get_schedule(int(offset))
    

    @handle_logs_and_exceptions
    def shipping_day(self, offset=0):
        return self.service.get_day_shippings(int(offset))
    
    
    @handle_logs_and_exceptions
    def user_login(self, request):
        if validation_error := validate_request(
            request, 
            {"document", "password"}
        ):
            return validation_error, 400
        
        document = request.get("document")
        password = request.get("password")

        user, user_status = self.service.get_user_by_document(document)
        if user_status == 500:
            return user, user_status
        
        if user_status == 400:
            return "DNI o contraseña incorrecta", user_status
        
        if user.levels == 1:
            return "No cuentas con acceso al sistema", 400

        if bcrypt.check_password_hash(user.password.encode('utf-8'), password.encode('utf-8')):
            access_token = create_access_token(identity=str(user.id))

            data = user.to_dict(exclude_fields=['password', 'stamp'])
            data.update({
                "token": access_token
            })
            return data, 200
        
        return "DNI o contraseña incorrecta", 400
    

    def webhook(self, request):
        mode = request.get('hub.mode')
        challenge = request.get('hub.challenge')
        verify_token = request.get('hub.verify_token')
        logging.info(f"Webhook received - mode: {mode}, challenge: {challenge}, verify_token: {verify_token}")

        if verify_token == "15KrEaR073D23":
            return challenge, 200
        else:
            return "Invalid token", 403
        

    @handle_logs_and_exceptions
    def webhook_data(self, request):
        #logging.info(request)
        return True, 200

        #para que se vaya trabajando como pubvlicidad y que las persons seten su cuenta en dale con bnka

        #EAAJQ9QIvTrABOzc1ccoAapvMK7aY8oWk9PR9nOqnP4BAdMI8aEZBVHWqUFuAJUvZAcy11qlDRJkyHDHIJuoBiI2PDVZAstN3XLvkZCPdyGJTyyCoKVt7N32C5gDKzzsmV4v8erSKRsYjtGYZBtVMicCUAHyxO37nOvuyPHtaGqCBrkw3ZCQDMEv6zfl94aYSYsWQZDZD