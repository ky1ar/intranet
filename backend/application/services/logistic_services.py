import logging
import firebase_admin
import threading

from firebase_admin import messaging, credentials
from datetime import date, datetime, timezone, timedelta
from application.models import  ShippingHistory, ShippingStatusList, FireCloudTokens, HistoryType
from application.handlers import handle_exceptions, handle_db_exceptions
from application.repository.logistic_repository import LogisticRepository
from application.repository.client_repository import ClientRepository
from application.proxy.whatsapp import Whatsapp
from flask import g
from application import socketio


class LogisticService:
    def __init__(self):
        self.check_firebase_initialized()
        self.logistic_repository = LogisticRepository()
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
    def get_schedule(self, offset):
        start_date, end_date = self._get_schedule_range(offset)
        
        scheduled_shippings, status = self.logistic_repository.get_scheduled_shippings(start_date, end_date)
        if status != 200:
            return scheduled_shippings, status

        orders_data = [self._format_shipping_data(s) for s in scheduled_shippings]
        schedule_by_day = self._group_orders_by_day(start_date, 6, orders_data)

        return schedule_by_day, 200


    @handle_exceptions
    def get_day_shippings(self, offset):
        day_of_interest = date.today() + timedelta(days=offset)
        day_str = day_of_interest.strftime("%Y-%m-%d")
        day_name = self._get_day_name_es(day_of_interest, True)
        day_name_with_number = f"{day_name} {day_of_interest.day}"

        scheduled_orders, status = self.logistic_repository.get_scheduled_shippings(day_of_interest, day_of_interest)
        if status != 200:
            return scheduled_orders, status

        orders_data = [self._format_shipping_data(s) for s in scheduled_orders]
        
        schedule_orders = {}
        for order in orders_data:
            schedule_orders.setdefault(order["schedule_id"], []).append(order)

        return {
            "date": day_str,
            "day_name": day_name_with_number,
            "orders": {
                f"schedule_{k}": v for k, v in schedule_orders.items()
            }
        }, 200


    def _get_schedule_range(self, offset):
        today = date.today()
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
        return start_date + timedelta(weeks=offset), end_date + timedelta(weeks=offset)


    def _format_shipping_data(self, shipping):
        register_date = shipping.register_date.strftime("%Y-%m-%d")
        delivery_date = shipping.delivery_date.strftime("%Y-%m-%d")
        client = shipping.client_order.client

        return {
            "shipping_order_id": shipping.id,
            "address": shipping.address.title(),
            "register_date": register_date,
            "delivery_date": delivery_date,
            "district_name": shipping.district.name,
            "order_number": shipping.client_order.number,
            "method_name": shipping.method.name,
            "method_background": shipping.method.background,
            "method_border": shipping.method.border,
            "method_slug": shipping.method.slug,
            "schedule_name": shipping.schedule.name,
            "schedule_id": shipping.schedule_id,
            "status_id": shipping.status_id,
            "status_name": shipping.status.name,
            "client_name": client.name.title() if client.name else "",
            "client_document": client.document,
            "client_email": client.email,
            "client_phone": client.phone[2:] if client.phone and len(client.phone) > 2 else client.phone,
            "client_id": client.id,
            "driver_id": shipping.driver_id,
            "driver_name": self._format_name(shipping.driver.name)
        }


    def _format_name(self, full_name):
        words = full_name.strip().split()

        if len(words) == 3:
            return f"{words[0]} {words[1]}"
        elif len(words) == 4:
            return f"{words[0]} {words[2]}"
        elif len(words) == 5:
            return f"{words[0]} {words[3]}"
        return "Texto no válido"
    

    def _group_orders_by_day(self, start_date, days, orders_data):
        schedule_by_day = []
        for i in range(days):
            day = start_date + timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            day_name_es = self._get_day_name_es(day)
            day_name_with_number = f"{day_name_es} {day.day}"

            day_orders = [o for o in orders_data if o["delivery_date"] == day_str]

            schedule_orders = {}
            for order in day_orders:
                schedule_orders.setdefault(order["schedule_id"], []).append(order)

            schedule_by_day.append({
                "date": day_str,
                "day_name": day_name_with_number,
                "orders": {
                    f"schedule_{k}": v for k, v in schedule_orders.items()
                }
            })

        return schedule_by_day


    def _get_day_name_es(self, date_obj, full=False):
        DAYS_IN_SPANISH = {
            "Monday": "lun", "Tuesday": "mar", "Wednesday": "mié",
            "Thursday": "jue", "Friday": "vie", "Saturday": "sáb", "Sunday": "dom"
        }
        if full:
            DAYS_IN_SPANISH = {
                "Monday": "lunes", "Tuesday": "martes", "Wednesday": "miércoles",
                "Thursday": "jueves", "Friday": "viernes", "Saturday": "sábado", "Sunday": "domingo"
            }
        return DAYS_IN_SPANISH.get(date_obj.strftime("%A"), date_obj.strftime("%A"))


    @handle_exceptions
    def get_orders_by_status(self, status_id):
        shipping_orders, status = self.logistic_repository.get_orders_by_status(status_id)
        if status != 200:
            return shipping_orders, status
        
        result = []
        for shipping in shipping_orders:
            register_date = shipping.register_date.strftime("%Y-%m-%d")
            client = shipping.client_order.client

            order_data = {
                "shipping_order_id": shipping.id,
                "address": shipping.address.title(),
                "register_date": register_date,
                "district_name": shipping.district.name,
                "order_number": shipping.client_order.number,
                "method_name": shipping.method.name,
                "method_slug": shipping.method.slug,
                "method_background": shipping.method.background,
                "method_border": shipping.method.border,
                "status_id": shipping.status_id,
                "client_name": client.name.title() if client.name else "",
                "client_document": client.document,
                "client_email": client.email,
                "client_phone": client.phone[2:] if client.phone and len(client.phone) > 2 else client.phone,
                "client_id": client.id
            }

            result.append(order_data)
        return result, 200

    
    @handle_exceptions
    def shipping_by_id(self, shipping_order_id):
        return self.logistic_repository.get_shipping_by_id(shipping_order_id)


    @handle_exceptions
    def shipping_by_order_number(self, order_number):
        return self.logistic_repository.get_shipping_by_order_number(order_number)
      
    
    @handle_exceptions
    def shipping_by_client_order_id(self, client_order_id):
        return self.logistic_repository.get_shipping_by_client_order_id(client_order_id)
    

    @handle_exceptions
    def get_shipping_order(self, shipping_order):
        client = shipping_order.client_order.client

        result = shipping_order.to_dict()
        result.update({
            "shipping_order_id": shipping_order.id,
            "address": shipping_order.address.title(),
            "district_name": shipping_order.district.name,
            "driver_name": shipping_order.driver.name,
            "method_name": shipping_order.method.name,
            "method_background": shipping_order.method.background,
            "method_border": shipping_order.method.border,
            "register_date_format": shipping_order.register_date.strftime("%Y-%m-%d"),
            "client_name": client.name.title() if client.name else "",
            "client_document": client.document,
            "client_email": client.email,
            "client_phone": client.phone[2:] if client.phone and len(client.phone) > 2 else client.phone,
            "client_id": client.id,
            "order_number": shipping_order.client_order.number
        })

        shipping_dates, shipping_dates_status = self.get_shipping_dates(shipping_order.id, shipping_order.status_id)
        if shipping_dates_status != 200:
            return shipping_dates, shipping_dates_status
        
        if shipping_order.status_id == 3:
            result["on_the_way_date"] = shipping_dates.get("on_the_way_date")
        if shipping_order.status_id == 4:
            result["on_the_way_date"] = shipping_dates.get("on_the_way_date")
            result["delivered_date"] = shipping_dates.get("delivered_date")
        elif shipping_order.status_id == 6:
            result["on_the_way_date"] = shipping_dates.get("on_the_way_date")
            result["not_delivered_date"] = shipping_dates.get("not_delivered_date")
        return result, 200


    @handle_exceptions
    def order_set(self, shipping_order, data):
        user_id = data.get("user_id")
        delivery_date = data.get("delivery_date")
        shipping_order_id = data.get("shipping_order_id")
        status_id = data.get("status_id")
        client = shipping_order.client_order.client

        logging.info(shipping_order.assigned.phone)
        if status_id in (2, 3, 4, 6):
            payload = {
                "phone": client.phone,
                "username": client.name.title(),
                "order_number": shipping_order.client_order.number,
                "schedule_id": shipping_order.schedule_id,
                "file": shipping_order.proof_photo,
                "delivery_date": delivery_date,
            }
            if shipping_order.method_id < 3:
                threading.Thread(target=self.whatsapp.logistic_status_change, args=(payload, status_id)).start()

        status_map = {
            1: ShippingStatusList.PENDING,
            2: ShippingStatusList.SCHEDULED,
            3: ShippingStatusList.ON_THE_WAY,
            4: ShippingStatusList.DELIVERED,
            6: ShippingStatusList.NOT_DELIVERED,
        }
        status = status_map.get(status_id)
        update_shipping, update_status = self.logistic_repository.update_shipping_order(shipping_order, data)
        if update_status != 200:
            return update_shipping, update_status
        
        socketio.emit("logistics_update_dashboard", {})
        socketio.emit("logistics_update_driver", {})

        history, history_status = self.logistic_repository.add_shipping_history(user_id, shipping_order_id, HistoryType.STATUS_CHANGE, status, data=update_shipping)
        if history_status != 200:
            return history, history_status
        
        return "Orden actualizada correctamente", 200
    

    @handle_exceptions
    def edit_shipping_order(self, shipping_order, data):
        user_id = data.get("user_id")
        shipping_order_id = data.get("shipping_order_id")
        method_id = data.get("method_id")
        register_date = data.get("register_date")
        district_id = data.get("district_id")
        address = data.get("address", "").strip()
        client_data = data.pop("client")
        client_id = shipping_order.client_order.client_id
        
        if not method_id:
            return "Seleccione un tipo de envío", 400
        if not register_date:
            return "Ingrese la fecha de registro", 400
        if not address:
            return "Ingrese la dirección", 400
        if not district_id:
            return "Seleccione un distrito", 400
    
        update_shipping, update_status = self.logistic_repository.update_shipping_order(shipping_order, data)
        if update_status != 200:
            return update_shipping, update_status
        
        client, client_status = self.client_repository.get_client_by_id(client_id)
        if client_status != 200:
            return client, client_status
        self.client_repository.update_client(client, client_data)

        socketio.emit("logistics_update_dashboard", {})
        socketio.emit("logistics_update_driver", {})

        history, history_status = self.logistic_repository.add_shipping_history(user_id, shipping_order_id, HistoryType.UPDATED, data=update_shipping)
        if history_status != 200:
            return history, history_status
        
        return "Orden actualizada correctamente", 200


    @handle_exceptions
    def new_shipping_order(self, data):
        client_order_id = data.get("client_order_id")
        order_number = data.get("order_number", "").strip()
        method_id = data.get("method_id")
        user_id = data.get("user_id")
        register_date = data.get("register_date")
        district_id = data.get("district_id")
        address = data.get("address", "").strip()

        if not client_order_id:
            if not order_number:
                return "Ingrese el número de orden", 400

            client_id = data.get("client_id")
            client_data = data.pop("client")

            document = client_data.get("document", "").strip()
            name = client_data.get("name", "").strip()
            phone = client_data.get("phone", "").strip()

            if not method_id:
                return "Seleccione un tipo de envío", 400
            if not register_date:
                return "Ingrese la fecha de registro", 400
            if not address:
                return "Ingrese la dirección", 400
            if not district_id:
                return "Seleccione un distrito", 400
            
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
                    return "Ingrese un celular válido", 400
                
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
                    
            client_order, client_order_status = self.client_repository.add_client_order(order_number, client_id)
            if client_order_status != 200:
                return client_order, client_order_status
            data["client_order_id"] = client_order
        else:
            find, find_status = self.logistic_repository.get_shipping_by_client_order_id(client_order_id)
            if find_status == 500:
                return find, find_status
            if find_status == 200:
                return "La Orden ya ha sido registrada", 400

        if not method_id:
            return "Seleccione un tipo de envío", 400
        if not register_date:
            return "Ingrese la fecha de registro", 400
        if not address:
            return "Ingrese la dirección", 400
        if not district_id:
            return "Seleccione un distrito", 400
    
        shipping_order_id, shipping_order_status = self.logistic_repository.add_shipping_order(data)
        if shipping_order_status != 200:
            return shipping_order_id, shipping_order_status

        socketio.emit("logistics_update_dashboard", {})
        socketio.emit("logistics_update_driver", {})
        history, history_status = self.logistic_repository.add_shipping_history(user_id, shipping_order_id, HistoryType.ADDED, ShippingStatusList.PENDING, data=data)
        if history_status != 200:
            return history, history_status
        return "Orden registrada correctamente", 200
    

    @handle_exceptions
    def delete_shipping_order(self, shipping_order, data):
        user_id = data.get("user_id")
        shipping_order_id = data.get("shipping_order_id")
        delete_shipping, delete_shipping_status = self.logistic_repository.delete_shipping_order(shipping_order)
        if delete_shipping_status != 200:
            return delete_shipping, delete_shipping_status
        
        socketio.emit("logistics_update_dashboard", {})
        socketio.emit("logistics_update_driver", {})
        history, history_status = self.logistic_repository.add_shipping_history(user_id, shipping_order_id, HistoryType.DELETED)
        if history_status != 200:
            return history, history_status
        return "Orden eliminada correctamente", 200


    @handle_db_exceptions
    def get_shipping_dates(self, order_id, status_id):
        statuses_to_fetch = [ShippingStatusList.ON_THE_WAY]
        
        if status_id == 4:
            statuses_to_fetch.append(ShippingStatusList.DELIVERED)
        elif status_id == 6:
            statuses_to_fetch.append(ShippingStatusList.NOT_DELIVERED)
        
        history_entries = (
            g.db_session.query(ShippingHistory)
            .filter(ShippingHistory.shipping_order_id == order_id)
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


    @handle_exceptions
    def photo_upload(self, shipping_order, data):
        user_id = data.get("user_id")
        shipping_order_id = data.get("shipping_order_id")
        update_shipping, update_status = self.logistic_repository.update_shipping_order(shipping_order, data)
        if update_status != 200:
            return update_shipping, update_status
        
        socketio.emit("logistics_update_dashboard", {})
        socketio.emit("logistics_update_driver", {})
        history, history_status = self.logistic_repository.add_shipping_history(user_id, shipping_order_id, HistoryType.UPDATED, data=update_shipping)
        if history_status != 200:
            return history, history_status
        
        return "Orden actualizada correctamente", 200
    

    @handle_exceptions
    def history(self, data):
        page = data.get("page")
        per_page = data.get("per_page")
        shipping_orders, shipping_orders_status = self.logistic_repository.get_all_shipping_orders(page=page, per_page=per_page)
        if shipping_orders_status != 200:
            return shipping_orders, shipping_orders_status
        
        list = []
        for order in shipping_orders["list"]:
            order_data = {
                "id": order.id,
                "order_number": order.client_order.number,
                "client_name": order.client_order.client.name.title(),
                #"technician_name": order.technician.name.title(),
                "method_id": order.method_id,
                "method_name": order.method.name,
                "status_id": order.status_id,
                "status_name": order.status.name,
                "finished": False if order.status_id < 4 else True,
                "register_date": self.date_format(order.register_date)
            }
            list.append(order_data)

        return {
            "list": list,
            "pagination": {
                "total": shipping_orders["total"],
                "page": shipping_orders["page"],
                "per_page": shipping_orders["per_page"],
                "pages": shipping_orders["pages"],
            }
        }, 200


    @handle_exceptions
    def statistics(self):
        total_orders, total_orders_code = self.logistic_repository.get_total_orders() 
        if total_orders_code != 200:
            return total_orders, total_orders_code
        
        today_orders, today_orders_code = self.logistic_repository.get_today_total_orders() 
        if today_orders_code != 200:
            return today_orders, today_orders_code
        
        week_orders, week_orders_code = self.logistic_repository.get_week_total_orders() 
        if week_orders_code != 200:
            return week_orders, week_orders_code

        month_orders, month_orders_code = self.logistic_repository.get_month_total_orders() 
        if month_orders_code != 200:
            return month_orders, month_orders_code

        orders_by_type, orders_by_type_code = self.logistic_repository.get_orders_by_type() 
        if orders_by_type_code != 200:
            return orders_by_type, orders_by_type_code
        by_status = [
            {"status_id": sid, "status": name, "count": count}
            for sid, name, count in orders_by_type
        ]

        orders_by_month, orders_by_month_code = self.logistic_repository.get_orders_by_month() 
        if orders_by_month_code != 200:
            return orders_by_month, orders_by_month_code
        by_month = [
            {'period': f"{self.months.get(int(period.split('-')[1]), 'Mes inválido')}", 'count': count}
            for period, count in orders_by_month
        ]
        
        orders_by_district, orders_by_district_code = self.logistic_repository.get_orders_by_district() 
        if orders_by_district_code != 200:
            return orders_by_district, orders_by_district_code
        by_tech = [
            {'technician': name, 'count': count}
            for name, count in orders_by_district
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
        
        orders, orders_status = self.logistic_repository.get_orders_like(order_number)
        if orders_status != 200:
            return orders, orders_status
        
        orders_list = [
            {
                "id": order.id,
                "order_number": order.client_order.number,
                "client_name": order.client_order.client.name.title(),
                "method_background": order.method.background,
                "method_border": order.method.border,
                "district_name": order.district.name.title(),

            } for order in orders
        ]
        return orders_list, 200


































    
    @handle_exceptions
    def check_firebase_initialized(self):
        if not firebase_admin._apps:
            cred = credentials.Certificate('serviceAccountKey.json')
            firebase_admin.initialize_app(cred)


    @handle_db_exceptions
    def get_fcm_token(self, token):
        token = g.db_session.query(FireCloudTokens).filter_by(token=token).first()
        if not token:
            return None, 400

        return token, 200


    @handle_db_exceptions
    def set_fcm_token(self, stored_token, user_id):
        stored_token.user_id = user_id
        g.db_session.add(stored_token)
        g.db_session.commit()
        return True, 200
    

    @handle_db_exceptions
    def revome_fcm_token(self, stored_token):
        stored_token.user_id = None
        g.db_session.add(stored_token)
        g.db_session.commit()
        return True, 200


    @handle_db_exceptions
    def register_token(self, data):
        utc_now = datetime.now(timezone.utc)
        peru_time = utc_now - timedelta(hours=5)

        user_id = data.get("user_id")
        device_id = data.get("device_id")
        token = data.get("token")
        old_token = data.get("old_token")

        if old_token:
            stored_token, stored_token_status = self.get_fcm_token(old_token)
            if stored_token_status != 200:
                return stored_token, stored_token_status
            
            stored_token.token = token
            stored_token.updated_at = peru_time

        else:
            new_fcm_token = FireCloudTokens(
                user_id=user_id,
                device_id=device_id,
                token=token,
                created_at=peru_time
            )
            g.db_session.add(new_fcm_token)

        g.db_session.commit()
        return True, 200
    

    @handle_db_exceptions
    def send_notification(self, shipping_order):
        status_id = shipping_order.status_id
        if status_id == 1:
            return True, 200
        
        vendor_id = shipping_order.vendor_id
        order_number = shipping_order.order_number
        vendor_name = shipping_order.vendor.name.split()[0]
        date_obj = datetime.strptime(str(shipping_order.delivery_date), "%Y-%m-%d")
        schedule_name = shipping_order.schedule.name

        months = {
            1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
            5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
            9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
        }
        
        if status_id == 2:
            title = f"Orden {order_number} programada"
            body = f"Hola {vendor_name}, la orden {order_number} ha sido programada para el {date_obj.day} de {months[date_obj.month]} en el turno {schedule_name}."
        if status_id == 3:
            title = f"Orden {order_number} en camino a su destino"
            body = f"Hola {vendor_name}, la orden {order_number} se encuentra en camino a su destino."
        if status_id == 4:
            title = f"Orden {order_number} entregada"
            body = f"Hola {vendor_name}, la orden {order_number} ha sido entregada con éxito."
        if status_id == 6:
            title = f"Orden {order_number} no entregada"
            body = f"Hola {vendor_name}, la orden {order_number} no ha podido ser entregada y tiene que repogramarse."
        
        tokens = g.db_session.query(FireCloudTokens.token).filter(FireCloudTokens.user_id == vendor_id).all()
        #tokens = g.db_session.query(FireCloudTokens.token).filter(FireCloudTokens.user_id.isnot(None)).all()

        tokens = [t[0] for t in tokens if t[0].strip()]

        if not tokens:
            logging.warning("No hay tokens registrados para enviar notificaciones")
            return "No hay dispositivos registrados", 400

        logging.info(f"Enviando a {len(tokens)} dispositivos")

        message = messaging.MulticastMessage(
            data={ 
                "title": title,
                "body": body
            },
            tokens=tokens
        )

        response = messaging.send_each_for_multicast(message)
        logging.info(f"Notificaciones enviadas: {response.success_count}, fallidas: {response.failure_count}")

        invalid_tokens = [
            tokens[i] for i, result in enumerate(response.responses)
            if not result.success and result.exception
        ]

        if invalid_tokens:
            logging.info(f"Eliminando {len(invalid_tokens)} tokens inválidos de la BD")
            g.db_session.query(FireCloudTokens).filter(
                FireCloudTokens.token.in_(invalid_tokens)
            ).delete(synchronize_session=False)
            g.db_session.commit()
            
        return True, 200

