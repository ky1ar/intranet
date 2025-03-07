import logging
import requests
import json

from application import redis_client
from config import WABA, ApisNet, Config
from datetime import date, datetime, timezone, timedelta
from application.models import Users, ShippingOrders, ShippingDistricts, ShippingMethod, ShippingContact, ShippingHistory, ShippingStatusList
from application.handlers import handle_exceptions, handle_db_exceptions
from sqlalchemy.orm import joinedload
from sqlalchemy import asc
from flask import g
from application import socketio


class BaseService:

    #def __init__(self):
        #self.sms_repository = SmsRepository()

    def post_waba(self, payload):
        url = f"{WABA.URL}"

        headers = {
            "Authorization": f"Bearer {WABA.TOKEN}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response_data = response.json()
        
        if response.status_code != 200:
            return f"Error {response_data}", response.status_code
        
        return "Mensaje enviado correctamente", 200
            

    @handle_exceptions
    def send_message(self, data, template_id):
        phone = data.get("phone")
        username = data.get("username")
        order_number = data.get("order_number")
        schedule_id = data.get("schedule_id")
        file = data.get("file")

        template_list = {
            3: "entrega",
            4: "entrega_exitosa_img",
            6: "no_entrega_img",
        }

        template_name = template_list.get(template_id)
        schedules = {
            1: (Config.T1_START, Config.T1_END),
            2: (Config.T2_START, Config.T2_END)
        }
        start, end = schedules.get(schedule_id)
        timer = 10

        mantra = Config.CONTACT_PHONE
        link = Config.REVIEW_URL
        base_url = Config.BASE_URL
        parameters = [{"type": "text", "parameter_name": "username", "text": username}]

        if template_id == 3:
            parameters.extend([
                {"type": "text", "parameter_name": "order_number", "text": order_number},
                {"type": "text", "parameter_name": "start", "text": start},
                {"type": "text", "parameter_name": "end", "text": end},
                {"type": "text", "parameter_name": "timer", "text": timer}
            ])
        elif template_id == 4:
            parameters.extend([
                {"type": "text", "parameter_name": "number", "text": mantra},
                {"type": "text", "parameter_name": "link", "text": link}
            ])
        elif template_id == 6:
            parameters.append({"type": "text", "parameter_name": "order_number", "text": order_number})

        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": "es_PE"},
                "components": [{"type": "body", "parameters": parameters}]
            }
        }

        if template_id in {4, 6} and file:
            header_component = {
                "type": "header",
                "parameters": [
                    {
                        "type": "image",
                        "image": {
                            "link": f"{base_url}{file}"
                        }
                    }
                ]
            }
            payload["template"]["components"].insert(0, header_component)

        return self.post_waba(payload)
    

    @handle_db_exceptions
    def get_user_by_email(self, email):
        user = g.db_session.query(Users).filter_by(email=email).first()
        if not user:
            return 'DNI o contraseña incorrecta', 400

        return user, 200


    def get_apis(self, path, params):
        url = f"{ApisNet.URL}{path}"

        headers = {
            "Authorization": f"Bearer {ApisNet.TOKEN}",
            "Referer": "python-requests"
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json(), 200
        elif response.status_code == 422:
            logging.warning(f"{response.url} - invalida params", params=params)
            logging.warning(response.text)
        elif response.status_code == 403:
            logging.warning(f"{response.url} - IP blocked")
        elif response.status_code == 429:
            logging.warning(f"{response.url} - Many requests add delay")
        elif response.status_code == 401:
            logging.warning(f"{response.url} - Invalid token or limited")
        else:
            logging.warning(f"{response.url} - Server Error status_code={response.status_code}")
        return None, 400
    

    def get_person(self, dni):
        return self.get_apis("/v2/reniec/dni", {"numero": dni})

    def get_company(self, ruc):
        return self.get_apis("/v2/sunat/ruc", {"numero": ruc})
    

    @handle_db_exceptions
    def get_user(self, document):
        if len(document) not in (8, 11):
            return "Documento inválido", 400
        
        user_key = f"user:{document}"
        user_cache = redis_client.get(user_key)
        if user_cache:
            logging.info('From redis')
            return json.loads(user_cache), 200
        
        user = g.db_session.query(Users).filter_by(document=document).first()
        if user:
            user_data = user.to_dict(exclude_fields=['password', 'stamp'])
            if 'phone' in user_data and user_data['phone']:
                user_data['phone'] = user_data['phone'][2:]
            redis_client.set(user_key, json.dumps(user_data))
            return user_data, 200

        document_key = f"document:{document}"
        document_cache = redis_client.get(document_key)
        if document_cache:
            logging.info('From redis')
            return {"name": document_cache}, 200
        
        if len(document) == 8:
            person, person_status = self.get_person(document)
            if person_status != 200:
                return person, person_status
            
            name = f"{person.get('nombres')} {person.get('apellidoPaterno')} {person.get('apellidoMaterno')}"
            formated = name.title()
            redis_client.set(document_key, formated)
            return {"name": formated}, 200
        
        company, company_status = self.get_company(document)
        if company_status != 200:
            return company, company_status
        
        formated = company.get('razonSocial').title()
        redis_client.set(document_key, formated)
        return {"name": formated}, 200
    

    @handle_db_exceptions
    def get_user_by_document(self, document):
        user = g.db_session.query(Users).filter_by(document=document).first()
        if not user:
            return 'Usuario no encontrado', 400

        return user, 200


    @handle_db_exceptions
    def get_user_by_id(self, user_id):
        user = g.db_session.query(Users).filter_by(id=user_id).first()
        if not user:
            return 'Usuario no encontrado', 400
        
        return user, 200
    

    @handle_db_exceptions
    def add_client(self, client):
        utc_now = datetime.now(timezone.utc)
        peru_time = utc_now - timedelta(hours=5)

        new_client = Users(
            levels=1,
            document=client.get("document"),
            name=client.get("name"),
            email=client.get("email"),
            phone=f'51{client.get("phone")}',
            password="password",
            stamp=peru_time,
        )

        g.db_session.add(new_client)
        g.db_session.flush()
        client_id = new_client.id
        g.db_session.commit()
        logging.info(f"New client added to DB with id {client_id}")
        return client_id, 200
    

    @handle_db_exceptions
    def update_client(self, client, data):
        client.email = data.get("email")
        client.phone = f'51{data.get("phone")}'

        g.db_session.add(client)
        g.db_session.commit()
        user_key = f"user:{client.document}"
        redis_client.delete(user_key)   
        return "Cliente actualizado correctamente", 200
    

    @handle_db_exceptions
    def get_shipping_by_order_number(self, order_number):
        purchase_order = (
            g.db_session.query(ShippingOrders)
            .filter(ShippingOrders.order_number == order_number)
            .filter(ShippingOrders.is_deleted.is_(False))
            .options(
                joinedload(ShippingOrders.contacts).joinedload(ShippingContact.client)
            )
            .first()
        )
            
        if not purchase_order:
            return 'Orden de pedido no encontrada', 400
        
        return purchase_order, 200


    @handle_db_exceptions
    def get_shipping_dates(self, order_id, status_id):
        statuses_to_fetch = [ShippingStatusList.ON_THE_WAY]
        
        if status_id == 4:
            statuses_to_fetch.append(ShippingStatusList.DELIVERED)
        elif status_id == 6:
            statuses_to_fetch.append(ShippingStatusList.NOT_DELIVERED)
        else:
            return None, 200
        
        history_entries = (
            g.db_session.query(ShippingHistory)
            .filter(ShippingHistory.order_id == order_id)
            .filter(ShippingHistory.status.in_(statuses_to_fetch))
            .order_by(ShippingHistory.created_at.desc())
            .all()
        )

        result = {
            "on_the_way_date": None,
            "delivered_date": None,
            "not_delivered_date": None
        }

        for entry in history_entries:
            if entry.status == ShippingStatusList.ON_THE_WAY:
                result["on_the_way_date"] = entry.created_at.strftime("%Y-%m-%d %H:%M:%S")
            elif entry.status == ShippingStatusList.DELIVERED:
                result["delivered_date"] = entry.created_at.strftime("%Y-%m-%d %H:%M:%S")
            elif entry.status == ShippingStatusList.NOT_DELIVERED:
                result["not_delivered_date"] = entry.created_at.strftime("%Y-%m-%d %H:%M:%S")

        return result, 200
    

    @handle_db_exceptions
    def add_shipping_order(self, data):

        new_shipping_order = ShippingOrders(
            order_number=data.get("order_number"),
            #client_id=data.get("client_id"),
            method_id=data.get("method_id"),
            driver_id=data.get("driver_id"),
            vendor_id=data.get("vendor_id"),
            admin_id=data.get("admin_id"),
            status_id=1,
            address=data.get("address"),
            district_id=data.get("district_id"),
            comments=data.get("comments"),
            register_date=data.get("register_date"),
        )

        g.db_session.add(new_shipping_order)
        g.db_session.flush()
        shipping_order_id = new_shipping_order.id
        g.db_session.commit()
        logging.info(f"New shipping order added to DB with id {shipping_order_id}")
        return shipping_order_id, 200


    @handle_db_exceptions
    def add_history(self, admin_id, order_id, history_type, status=None, data=None):
        utc_now = datetime.now(timezone.utc)
        peru_time = utc_now - timedelta(hours=5)

        new_history = ShippingHistory(
            admin_id=admin_id,
            order_id=order_id,
            type=history_type,
            created_at=peru_time
        )
        if status:
            new_history.status = status
        if data:
            new_history.data = data

        g.db_session.add(new_history)
        g.db_session.commit()
        logging.info(f"New history added to DB")
        return True, 200


    @handle_db_exceptions
    def add_shipping_contact(self, shipping_order_id, client_id):
        #utc_now = datetime.now(timezone.utc)
        #peru_time = utc_now - timedelta(hours=5)

        new_shipping_contact = ShippingContact(
            order_id=shipping_order_id,
            client_id=client_id,
        )

        g.db_session.add(new_shipping_contact)
        g.db_session.commit()
        logging.info("New shipping contact added to DB")
        return True, 200
    

    @handle_db_exceptions
    def update_shipping_order_data(self, shipping, updated_fields):
        for field, value in updated_fields.items():
            setattr(shipping, field, value)
        g.db_session.add(shipping)
        g.db_session.commit()
        logging.info(f"Shipping order {shipping.order_number} updated: {updated_fields}")
        return True


    @handle_db_exceptions
    def update_shipping_order(self, order, data):
        if "delivery_date" in data:
            order.delivery_date = data["delivery_date"]
        if "status_id" in data:
            order.status_id = data["status_id"]
        if "schedule_id" in data:
            order.schedule_id = data["schedule_id"]
        if "proof_photo" in data:
            order.proof_photo = data["proof_photo"]

        g.db_session.add(order)
        g.db_session.commit()
        socketio.emit("update_schedule", {})
        return "Orden actualizada correctamente", 200
    

    @handle_db_exceptions
    def delete_shipping_order(self, shipping_order):
        shipping_order.is_deleted = True
        g.db_session.add(shipping_order)
        g.db_session.commit()
        socketio.emit("update_schedule", {})
        return "Orden eliminada correctamente", 200
    

    @handle_db_exceptions
    def get_scheduled_shippings(self, start_date, end_date):
        shipping_orders = (
            g.db_session.query(ShippingOrders)
            .filter(ShippingOrders.delivery_date >= start_date, ShippingOrders.delivery_date <= end_date)
            .filter(ShippingOrders.is_deleted.is_(False))
            .filter(ShippingOrders.status_id != 1)
            .options(
                joinedload(ShippingOrders.contacts).joinedload(ShippingContact.client)
            )
            .all()
        )
        
        result = []
        if not shipping_orders:
            return result, 200
        
        for shipping in shipping_orders:
            register_date = shipping.register_date.strftime("%Y-%m-%d")
            delivery_date = shipping.delivery_date.strftime("%Y-%m-%d")

            order_data = {
                "address": shipping.address.title(),
                "register_date": register_date,
                "delivery_date": delivery_date,
                "district_name": shipping.district.name,
                "order_number": shipping.order_number,
                "method_name": shipping.method.name,
                "method_background": shipping.method.background,
                "method_border": shipping.method.border,
                "method_slug": shipping.method.slug,
                "schedule_name": shipping.schedule.name,
                "schedule_id": shipping.schedule_id,
                "status_id": shipping.status_id,
                "status_name": shipping.status.name,
                "contacts": []
            }
            for contact in shipping.contacts:
                contact_data = {
                    "name": contact.client.name.title(),
                    "document": contact.client.document,
                    "email": contact.client.email,
                    "phone": contact.client.phone[2:],
                    "document_id": contact.client.id
                }
                order_data["contacts"].append(contact_data)

            result.append(order_data)

        return result, 200
    

    @handle_db_exceptions
    def get_orders_by_status(self, status_id):
        shipping_orders = (
            g.db_session.query(ShippingOrders)
            .filter(ShippingOrders.status_id == status_id)
            .filter(ShippingOrders.is_deleted.is_(False))
            .options(
                joinedload(ShippingOrders.contacts).joinedload(ShippingContact.client)
            )
            .order_by(asc(ShippingOrders.register_date))
            .all()
        )

        if not shipping_orders:
            return 'No se encontraron ordenes de pedido para este estado', 400
        
        result = []
        for shipping in shipping_orders:
            register_date = shipping.register_date.strftime("%Y-%m-%d")

            order_data = {
                "address": shipping.address.title(),
                #"client_name": shipping.client.name.title(),
                "register_date": register_date,
                "district_name": shipping.district.name,
                "order_number": shipping.order_number,
                "method_name": shipping.method.name,
                "method_slug": shipping.method.slug,
                "method_background": shipping.method.background,
                "method_border": shipping.method.border,
                "contacts": []
            }

            for contact in shipping.contacts:
                contact_data = {
                    "name": contact.client.name.title(),
                    "document": contact.client.document,
                    "email": contact.client.email,
                    "phone": contact.client.phone,
                    "document_id": contact.client.id
                }
                order_data["contacts"].append(contact_data)

            result.append(order_data)

        return result, 200
    

    @handle_db_exceptions
    def get_schedule(self, offset):
        DAYS_IN_SPANISH = {
            "Monday": "lun",
            "Tuesday": "mar",
            "Wednesday": "mié",
            "Thursday": "jue",
            "Friday": "vie",
            "Saturday": "sáb",
            "Sunday": "dom"
        }

        today = date.today()
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)

        start_date += timedelta(weeks=offset)
        end_date += timedelta(weeks=offset)

        scheduled_shippings, scheduled_shippings_status = self.get_scheduled_shippings(start_date, end_date)
        if scheduled_shippings_status != 200:
            return scheduled_shippings, scheduled_shippings_status
        
        schedule_by_day = []
        for i in range(6):
            day = start_date + timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            day_name = day.strftime("%A")
            day_name_es = DAYS_IN_SPANISH.get(day_name, day_name)

            day_name_with_number = f"{day_name_es} {day.day}"

            day_orders = [order for order in scheduled_shippings if order['delivery_date'] == day_str]

            schedule_orders = {1: [], 2: []}
            for order in day_orders:
                schedule_orders.setdefault(order["schedule_id"], []).append(order)
                
            schedule_by_day.append({
                "date": day_str,
                "day_name": day_name_with_number,
                "orders": {
                    "schedule_1": schedule_orders.get(1, []),
                    "schedule_2": schedule_orders.get(2, [])
                }
            })

        return schedule_by_day, 200
    

    @handle_db_exceptions
    def get_day_shippings(self, offset):
        DAYS_IN_SPANISH = {
            "Monday": "lunes",
            "Tuesday": "martes",
            "Wednesday": "miércoles",
            "Thursday": "jueves",
            "Friday": "viernes",
            "Saturday": "sábado",
            "Sunday": "domingo"
        }

        today = date.today()
        day_of_interest = today + timedelta(days=offset)
        day_str = day_of_interest.strftime("%Y-%m-%d")
        day_name = day_of_interest.strftime("%A")
        day_name_es = DAYS_IN_SPANISH.get(day_name, day_name)
        day_name_with_number = f"{day_name_es} {day_of_interest.day}"

        scheduled_orders, scheduled_orders_status = self.get_scheduled_shippings(day_of_interest, day_of_interest)
        if scheduled_orders_status != 200:
            return scheduled_orders, scheduled_orders_status
        
        day_orders = [order for order in scheduled_orders if order['delivery_date'] == day_str]

        schedule_orders = {1: [], 2: []}
        for order in day_orders:
            schedule_orders.setdefault(order["schedule_id"], []).append(order)

        return {
            "date": day_str,
            "day_name": day_name_with_number,
            "orders": {
                "schedule_1": schedule_orders.get(1, []),
                "schedule_2": schedule_orders.get(2, [])
            }
        }, 200


    @handle_db_exceptions
    def get_drivers(self):
        drivers = g.db_session.query(Users).filter_by(levels=5).all()
        if not drivers:
            return 'Drivers not found', 400
        
        return [driver.to_dict(exclude_fields=['password', 'stamp']) for driver in drivers], 200
    

    @handle_db_exceptions
    def get_vendors(self):
        vendors = g.db_session.query(Users).filter(Users.levels.in_([6, 3])).order_by(Users.name).all()
        if not vendors:
            return 'Vendors not found', 400
        
        return [vendor.to_dict(exclude_fields=['password', 'stamp']) for vendor in vendors], 200
    

    @handle_db_exceptions
    def get_districts(self):
        cache_key = "district:list"

        cached = redis_client.get(cache_key)
        if cached:
            logging.info('From redis')
            return json.loads(cached), 200 
        
        districts = g.db_session.query(ShippingDistricts).order_by(ShippingDistricts.name).all()
        if not districts:
            return 'Districts not found', 400
        
        districts_data = [district.to_dict() for district in districts]

        redis_client.setex(cache_key, 86400, json.dumps(districts_data)) #86400 dia #3600 hora #300 5

        return districts_data, 200


    @handle_db_exceptions
    def get_shipping_types(self):
        cache_key = "shipping_method:list"

        cached = redis_client.get(cache_key)
        if cached:
            logging.info('From redis')
            return json.loads(cached), 200 
        
        shipping_types = g.db_session.query(ShippingMethod).all()
        if not shipping_types:
            return 'Shipping Types not found', 400
        
        data = [shipping_type.to_dict() for shipping_type in shipping_types]
        redis_client.setex(cache_key, 86400, json.dumps(data))

        return data, 200