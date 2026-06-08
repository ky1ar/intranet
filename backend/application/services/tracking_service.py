import logging
import json
import threading
import time
from application.handlers import handle_exceptions
from application.repository.tracking_repository import TrackingRepository
from application.repository.user_repository import UserRepository
from application.repository.client_repository import ClientRepository
from application.services.clients_service import ClientsService
from application.repository.logistic_repository import LogisticRepository
from application.repository.general_repository import GeneralRepository
from application.models import ShippingStatusList
from application.proxy.shalom import Shalom
from application.proxy.olva import Olva
from application.proxy.marvisur import Marvisur
from application.proxy.whatsapp import Whatsapp
from application import socketio, redis_client


class TrackingService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.client_repository = ClientRepository()
        self.clients_service = ClientsService()
        self.tracking_repository = TrackingRepository()
        self.logistic_repository = LogisticRepository()
        self.general_repository = GeneralRepository()
        self.shalom = Shalom()
        self.olva = Olva()
        self.marvisur = Marvisur()
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


    def date_format_hour(self, fecha):
        if not fecha:
            return None

        dia = fecha.day
        mes = self.months[fecha.month]
        año = fecha.year

        show_time = False

        if hasattr(fecha, "hour"):
            if fecha.hour != 0 or fecha.minute != 0 or fecha.second != 0:
                show_time = True

        if show_time:
            hora = fecha.strftime('%I:%M %p').lower()
            return f"{dia} de {mes} de {año}, a las {hora}"

        return f"{dia} de {mes} de {año}"


    @handle_exceptions
    def add(self, data):
        client_order_id = data.get("client_order_id")
        order_number = data.get("order_number", "").strip()
        agency_id = int(data.get("agency_id"))
        code1 = data.get("code1")
        code2 = data.get("code2")

        if not agency_id:
            return "Seleccione una agencia", 400
        if not code1:
            return "Ingrese el código 1", 400
        if not code2:
            return "Ingrese el código 2", 400
        
        agency_clients = {
            1: self.shalom,
            2: self.olva,
            3: self.marvisur
        }

        tracking_client = agency_clients.get(agency_id)
        if not tracking_client:
            return "Agencia no soportada", 400

        tracking_data, tracking_status = tracking_client.tracking(code1, code2)
        if tracking_status != 200:
            return tracking_data, tracking_status
        
        client_id = data.get("client_id")
        client_data = data.pop("client")

        document = client_data.get("document", "").strip()
        name = client_data.get("name", "").strip()
        phone = client_data.get("phone", "").strip()
    
        if not client_order_id:
            if not order_number:
                return "Ingrese el número de orden", 400

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
            find, find_status = self.tracking_repository.get_tracking_order(client_order_id)
            if find_status == 500:
                return find, find_status
            if find_status == 200:
                return "La Orden ya ha sido registrada", 400

        tracking_order, tracking_order_status = self.tracking_repository.add_tracking_order(data, tracking_data)
        if tracking_order_status != 200:
            return tracking_order, tracking_order_status

        agency, agency_status = self.tracking_repository.get_agency(agency_id)
        if agency_status != 200:
            return agency, agency_status
        
        if not phone.startswith("51"):
            phone = f"51{phone}"

        payload = {
            "phone": phone,
            "client_name": name.title(),
            "order_number": order_number,
            "agency": agency.name,
            "agency_id": agency_id,
            "code1": data.get("code1"),
            "code2": data.get("code2"),
            "code3": data.get("code3", ""),
        }

        threading.Thread(target=self.whatsapp.tracking_alert, args=(payload,)).start()
            
        socketio.emit("update_tracking_orders", {})
        history, history_status = self.tracking_repository.add_tracking_history(tracking_order, tracking_data.get("status_data"))
        if history_status != 200:
            return history, history_status
        
        return "Orden registrada correctamente", 200
        

    @handle_exceptions
    def client_list(self, document):
        client, client_status = self.client_repository.get_client_by_document(document)
        if client_status != 200:
            return client, client_status
        
        orders, orders_status = self.client_repository.get_client_orders(client.id)
        if orders_status != 200:
            return orders, orders_status

        order_ids = [order.id for order in orders]

        # ----------------- TRACKING -----------------
        tracking_list, tracking_list_status = self.tracking_repository.get_list(order_ids)
        if tracking_list_status != 200:
            return tracking_list, tracking_list_status
        
        data = []
        for track in tracking_list:
            data.append({
                'id': track.id,
                'order_number': track.client_order.number,
                'client_name': client.name,
                'agency_id': track.agency_id,
                'destination_agency': track.destination_agency,
                'last_status': track.status.name,
                'last_status_id': track.status_id,
                'register_at': self.date_format_hour(track.register_at),
            })

        # ----------------- LOGISTIC -----------------
        logistic_list, logistic_list_status = self.logistic_repository.get_list(order_ids)
        if logistic_list_status != 200:
            return logistic_list, logistic_list_status
        
        STATUS_MAPPING = {
            1: (1, "En agencia"),
            2: (1, "En agencia"),
            3: (2, "En ruta"),
            4: (4, "Entregado")
        }

        AGENCY_ID_DEFAULT = 4

        for row in logistic_list:
            status_id, status_name = STATUS_MAPPING.get(row.status.id, (5, "No entregado"))
            if status_id > 4:
                continue

            data.append({
                'id': row.id,
                'order_number': row.client_order.number,
                'client_name': client.name,
                'agency_id': AGENCY_ID_DEFAULT,
                'destination_agency': f"{row.district.name}, Lima",
                'last_status': status_name,
                'last_status_id': status_id,
                'register_at': self.date_format_hour(row.register_date),
            })

        data.sort(key=lambda x: x['id'], reverse=True)

        # ----------------- AGRUPAR POR STATUS -----------------
        grouped = {}

        for item in data:
            status_id = item['last_status_id']
            status_name = item['last_status']

            if status_id not in grouped:
                grouped[status_id] = {
                    "status_id": status_id,
                    "status_name": status_name,
                    "tracking_order": []
                }

            grouped[status_id]["tracking_order"].append({
                "agency_id": item["agency_id"],
                "order_number": item["order_number"],
                "client_name": item["client_name"],
                "destination_agency": item["destination_agency"],
                "register_at": item["register_at"],
            })

        result = list(grouped.values())
        result.sort(key=lambda x: x["status_id"])

        return result, 200


    @handle_exceptions
    def dashboard(self):
        tracking_orders, tracking_orders_status = self.tracking_repository.get_all_list()
        if tracking_orders_status != 200:
            return tracking_orders, tracking_orders_status
        
        tracking_status, tracking_code = self.general_repository.get_tracking_status() 
        if tracking_code != 200:
            return tracking_status, tracking_code
        
        result = []
        for status in tracking_status:
            status_order = [tracking_order for tracking_order in tracking_orders if tracking_order.status_id == status.id]

            status_orders = []
            for order in status_order:
                tracking_order_data = {
                    'id': order.id,
                    'order_number': order.client_order.number,
                    'client_name': order.client_order.client.name,
                    'agency_id': order.agency_id,
                    'destination_agency': order.destination_agency,
                }
                status_orders.append(tracking_order_data)

            result.append({
                "status_id": status.id,
                "status_name": status.name,
                "tracking_order": status_orders
            })
        return result, 200


    @handle_exceptions
    def get_order_by_id(self, order_id):
        tracking_order, tracking_order_status = self.tracking_repository.get_tracking_order_by_id(order_id)
        if tracking_order_status != 200:
            return tracking_order, tracking_order_status
        
        tracking_history, tracking_history_status = self.tracking_repository.get_tracking_history(tracking_order.id)
        if tracking_history_status != 200:
            return tracking_history, tracking_history_status

        history_data = []
        for history in tracking_history:
            history_data.append({
                'status_name': history.status.name,
                'status_id': history.status_id,
                'register_at': history.register_at.strftime("%d-%m-%Y %I:%M %p"),
            })

        result = {
            #'agency_name': tracking_order.agency.name,
            'agency_id': tracking_order.agency_id,
            'code1': tracking_order.code1,
            'code2': tracking_order.code2,
            'code3': tracking_order.code3,
            'origin_agency': tracking_order.origin_agency,
            'client_name': tracking_order.client_order.client.name,
            'order_number': tracking_order.client_order.number,
            'client_document': tracking_order.client_order.client.document,
            'client_phone': tracking_order.client_order.client.phone,
            'destination_agency': tracking_order.destination_agency,
            'status_history': history_data
        }
        return result, 200
        

    @handle_exceptions
    def get_order(self, data):
        document = data.get("document")
        order_number = data.get("order_number")
        agency_id = data.get("agency_id")
        
        client, cc = self.client_repository.get_client_by_document(document)
        if cc != 200:
            return client, cc

        client_order, coc = self.client_repository.get_client_order(order_number, client.id)
        if coc != 200:
            return client_order, coc
        order_id = client_order.id

        if agency_id < 4:
            tracking_order, toc = self.tracking_repository.get_tracking_order(order_id)
            if toc != 200:
                return tracking_order, toc
            
            tracking_history, thc = self.tracking_repository.get_tracking_history(tracking_order.id)
            if thc != 200:
                return tracking_history, thc

            history_data = []
            for history in tracking_history:
                history_data.append({
                    'status_name': history.status.name,
                    'status_id': history.status_id,
                    'register_at': self.date_format_hour(history.register_at),
                })

            result = {
                'order_number': order_number,
                'agency_name': tracking_order.agency.name,
                'agency_id': tracking_order.agency_id,
                'code1': tracking_order.code1,
                'code2': tracking_order.code2,
                'code3': tracking_order.code3,
                'origin_agency': tracking_order.origin_agency,
                'destination_agency': tracking_order.destination_agency,
                'status_history': history_data
            }
            return result, 200
        
        shipping_order, soc = self.logistic_repository.get_shipping_by_client_order_id(order_id)
        if soc != 200:
            return shipping_order, soc
        
        shipping_history, shc = self.logistic_repository.get_shipping_history(shipping_order.id)
        if shc != 200:
            return shipping_history, shc
        
        history_data = []
        STATUS_MAPPING = {
            "PENDING": (1, "Registrado"),
            "SCHEDULED": (1, "Programado"),
            "ON_THE_WAY": (2, "En ruta"),
            "DELIVERED": (4, "Entregado"),
            "NOT_DELIVERED": (5, "No entregado"),
        }

        STATUS_ORDER = ["PENDING", "SCHEDULED", "ON_THE_WAY", "DELIVERED", "NOT_DELIVERED"]

        valid_history = [h for h in shipping_history if h.status]
        valid_history.sort(key=lambda h: h.created_at)
        last_status_entries = {}
        for h in valid_history:
            last_status_entries[h.status.value] = h

        final_status_value = None
        if valid_history:
            final_status_value = valid_history[-1].status.value

        show_history = []
        for status_key in STATUS_ORDER:
            if status_key in last_status_entries:

                h = last_status_entries[status_key]
                status_id, status_name = STATUS_MAPPING[status_key]
                show_history.append({
                    'status_name': status_name,
                    'status_id': status_id,
                    'register_at': self.date_format_hour(h.created_at) if status_key != "SCHEDULED" else self.date_format_hour(shipping_order.delivery_date),
                })
            if status_key == final_status_value:
                break

        result = {
            'agency_name': f"Krear 3D - {shipping_order.method.name}",
            'agency_id': 4,
            'origin_agency': "Lima",
            'order_number': shipping_order.client_order.number,
            'destination_agency': shipping_order.district.name,
            'status_history': show_history,
            'code1': "",
            'code2': "",
            'code3': "",
        }
        return result, 200
    

    @handle_exceptions
    def get_qr_data(self, ose_id):
        # La guía de Shalom es inmutable por ose_id; se cachea para evitar 429.
        # Un escaneo dispara varias consultas idénticas casi simultáneas, así que
        # además del cache se usa un lock (single-flight): solo el primer request
        # consulta Shalom y el resto espera a que llene el cache.
        key = f"qr_data:{ose_id}"
        lock_key = f"qr_data_lock:{ose_id}"

        tracking_data = None
        cache = redis_client.get(key)
        if not cache and redis_client.set(lock_key, "1", nx=True, ex=10):
            # Este request gana el lock: consulta Shalom y llena el cache.
            try:
                tracking_data, tracking_status = self.shalom.tracking_ose_id(ose_id)
                if tracking_status != 200:
                    return tracking_data, tracking_status
                redis_client.setex(key, 300, json.dumps(tracking_data))
            finally:
                redis_client.delete(lock_key)
        elif not cache:
            # Otro request ya está consultando Shalom; esperar a que cachee (~5s máx).
            for _ in range(50):
                time.sleep(0.1)
                cache = redis_client.get(key)
                if cache:
                    break

        if tracking_data is None:
            if cache:
                logging.info("QR data loaded from cache")
                tracking_data = json.loads(cache)
            else:
                # El lock expiró o la consulta previa falló; consultar directamente.
                tracking_data, tracking_status = self.shalom.tracking_ose_id(ose_id)
                if tracking_status != 200:
                    return tracking_data, tracking_status
                redis_client.setex(key, 300, json.dumps(tracking_data))

        client_data, client_status = self.clients_service.get_data(tracking_data.get("client_document"))
        if client_status == 200:
            tracking_data.update({
                "client_name": client_data.get("name"),
                "client_email": client_data.get("email"),
                "client_id": client_data.get("id"),
                "client_phone": client_data.get("phone"),
            })

        return tracking_data, 200
    

    @handle_exceptions
    def force(self, order_id):
        tracking_order, toc = self.tracking_repository.get_tracking_order_by_id(order_id)
        if toc != 200:
            return tracking_order, toc
        
        agency_clients = {
            1: self.shalom,
            2: self.olva,
            3: self.marvisur
        }
        agency_id = tracking_order.agency_id
            
        tracking_client = agency_clients.get(agency_id)
        if tracking_order.status_id < 4:
            if agency_id == 1:
                tracking_status, tsc = tracking_client.tracking_status(tracking_order.external_id)
            else:
                tracking_status, tsc = tracking_client.tracking(tracking_order.code1, tracking_order.code2)

            if tsc == 200:
                self.tracking_repository.update_tracking_order(tracking_order.id, tracking_status)
                self.tracking_repository.add_tracking_history(tracking_order.id, tracking_status.get("status_data"), tracking_order.status_id)
                
                return "Orden actualizada", 200

        return "Nada que actualizar", 200


    @handle_exceptions
    def force_all(self):
        tracking_orders, toc = self.tracking_repository.get_open_tracking_orders()
        if toc != 200:
            return tracking_orders, toc

        if not tracking_orders:
            return {"updated": [], "skipped": [], "message": "No hay órdenes pendientes"}, 200

        agency_clients = {
            1: self.shalom,
            2: self.olva,
            3: self.marvisur
        }

        updated = []
        skipped = []

        for tracking_order in tracking_orders:
            agency_id = tracking_order.agency_id
            tracking_client = agency_clients.get(agency_id)

            if not tracking_client:
                skipped.append({
                    "order_id": tracking_order.id,
                    "reason": f"Agencia {agency_id} sin cliente configurado"
                })
                continue

            if tracking_order.status_id >= 4:
                skipped.append({
                    "order_id": tracking_order.id,
                    "reason": "Orden ya entregada"
                })
                continue
            
            if agency_id == 1:
                tracking_status, tsc = tracking_client.tracking_status(tracking_order.external_id)
            else:
                tracking_status, tsc = tracking_client.tracking(tracking_order.code1, tracking_order.code2)

            if tsc == 200:
                self.tracking_repository.update_tracking_order(tracking_order.id, tracking_status)
                self.tracking_repository.add_tracking_history(
                    tracking_order.id,
                    tracking_status.get("status_data"),
                    tracking_order.status_id
                )
                updated.append(tracking_order.id)
                time.sleep(15)
            else:
                skipped.append({
                    "order_id": tracking_order.id,
                    "reason": f"Error al consultar agencia (status {tsc})"
                })

        if updated:
            socketio.emit("update_tracking_orders", {})

        return {
            "updated": updated,
            "skipped": skipped,
            "message": "Proceso de actualización masiva finalizado"
        }, 200
        
    
    @handle_exceptions
    def force_shalom(self, data):
        ose_id = data.get("ose_id")
        order_number = data.get("order_number")
        order_code = data.get("order_code")
        consult_type = data.get("consult_type")

        if consult_type == "status":
            return self.shalom.tracking_status(ose_id)
        elif consult_type == "codes":
            return self.shalom.tracking(order_number, order_code)
        
        return self.shalom.tracking_ose_id(ose_id)
        

    @handle_exceptions
    def history(self, data):
        page = data.get("page")
        per_page = data.get("per_page")
        tracking_orders, tracking_orders_status = self.tracking_repository.get_all_tracking_orders(page=page, per_page=per_page)
        if tracking_orders_status != 200:
            return tracking_orders, tracking_orders_status
        
        list = []
        for order in tracking_orders["list"]:
            order_data = {
                "id": order.id,
                "order_number": order.client_order.number,
                "client_name": order.client_order.client.name.title(),
                #"technician_name": order.technician.name.title(),
                "agency_id": order.agency_id,
                "agency_name": order.agency.name,
                "status_id": order.status_id,
                "finished": False if order.status_id < 4 else True,
                "register_at": self.date_format(order.register_at)
            }
            list.append(order_data)

        return {
            "list": list,
            "pagination": {
                "total": tracking_orders["total"],
                "page": tracking_orders["page"],
                "per_page": tracking_orders["per_page"],
                "pages": tracking_orders["pages"],
            }
        }, 200


    @handle_exceptions
    def statistics(self):
        total_orders, total_orders_code = self.tracking_repository.get_total_orders() 
        if total_orders_code != 200:
            return total_orders, total_orders_code
        
        today_orders, today_orders_code = self.tracking_repository.get_today_total_orders() 
        if today_orders_code != 200:
            return today_orders, today_orders_code
        
        week_orders, week_orders_code = self.tracking_repository.get_week_total_orders() 
        if week_orders_code != 200:
            return week_orders, week_orders_code

        month_orders, month_orders_code = self.tracking_repository.get_month_total_orders() 
        if month_orders_code != 200:
            return month_orders, month_orders_code

        orders_by_agency, orders_by_agency_code = self.tracking_repository.get_orders_by_agency() 
        if orders_by_agency_code != 200:
            return orders_by_agency, orders_by_agency_code
        by_agency = [
            {"agency_id": sid, "agency": name, "count": count}
            for sid, name, count in orders_by_agency
        ]

        orders_by_month, orders_by_month_code = self.tracking_repository.get_orders_by_month() 
        if orders_by_month_code != 200:
            return orders_by_month, orders_by_month_code
        by_month = [
            {'period': f"{self.months.get(int(period.split('-')[1]), 'Mes inválido')}", 'count': count}
            for period, count in orders_by_month
        ]
        
        orders_by_department, orders_by_department_code = self.tracking_repository.get_orders_by_department() 
        if orders_by_department_code != 200:
            return orders_by_department, orders_by_department_code
        by_department = [
            {'department': name, 'count': count}
            for name, count in orders_by_department
        ]
        result = {
            "count":  {
                "total": total_orders or 0,
                "today": today_orders or 0,
                "week": week_orders or 0,
                "month": month_orders or 0
            },
            "by_agency": by_agency,
            "by_month": by_month,
            "by_department": by_department,
        }
        return result, 200


    @handle_exceptions
    def find_orders(self, order_number):
        if len(order_number) < 2:
            return None, 400
        
        orders, orders_status = self.tracking_repository.get_orders_like(order_number)
        if orders_status != 200:
            return orders, orders_status
        
        orders_list = [
            {
                "id": order.id,
                "order_number": order.client_order.number,
                "client_name": order.client_order.client.name.title(),
                "agency_id": order.agency.id,

            } for order in orders
        ]
        return orders_list, 200