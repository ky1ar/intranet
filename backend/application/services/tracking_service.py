import logging

from datetime import date, datetime, timezone, timedelta
from application.handlers import handle_exceptions
from application.repository.tracking_repository import TrackingRepository
from application.repository.user_repository import UserRepository
from application.repository.client_repository import ClientRepository
from application.repository.logistic_repository import LogisticRepository
from application.proxy.shalom import Shalom
from application.proxy.olva import Olva
from application.proxy.marvisur import Marvisur


class TrackingService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.client_repository = ClientRepository()
        self.tracking_repository = TrackingRepository()
        self.logistic_repository = LogisticRepository()
        self.shalom = Shalom()
        self.olva = Olva()
        self.marvisur = Marvisur()


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
        
        if not client_order_id:
            if not order_number:
                return "Ingrese el número de orden", 400
            
            client_id = data.get("client_id")
            client_data = data.pop("client")

            document = client_data.get("document", "").strip()
            name = client_data.get("name", "").strip()
            phone = client_data.get("phone", "").strip()

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

        #socketio.emit("update_schedule", {})
        history, history_status = self.tracking_repository.add_tracking_history(tracking_order, tracking_data.get("status_data"))
        if history_status != 200:
            return history, history_status
        
        return "Orden registrada correctamente", 200
        

    @handle_exceptions
    def list(self, document):
        client, client_status = self.client_repository.get_client_by_document(document)
        if client_status != 200:
            return client, client_status
        
        orders, orders_status = self.client_repository.get_client_orders(client.id)
        if orders_status != 200:
            return orders, orders_status

        order_ids = [order.id for order in orders]

        tracking_list, tracking_list_status = self.tracking_repository.get_list(order_ids)
        if tracking_list_status != 200:
            return tracking_list, tracking_list_status
        
        data = []
        for track in tracking_list:
            data.append({
                'id': track.id,
                'order_number': track.client_order.number,
                'client_name': client.name,
                'client_document': client.document,
                #'agency': track.agency.name if track.agency else None,
                'agency_image': track.agency.image if track.agency else None,
                'agency_id': track.agency_id,
                #'agency_id': track.agency_id,
                'status': track.status.name if track.status else None,
                'status_id': track.status.id if track.status else None,
                'code1': track.code1,
                'code2': track.code2,
                'register_at': track.register_at.strftime("%d %B %Y %I:%M %p") if track.register_at else None
            })

        logistic_list, logistic_list_status = self.logistic_repository.get_list(order_ids)
        if logistic_list_status != 200:
            return logistic_list, logistic_list_status
        
        for row in logistic_list:
            data.append({
                'id': row.id,
                'order_number': row.client_order.number,
                'client_name': client.name,
                'client_document': client.document,
                #'agency': row.agency.name if row.agency else None,
                'agency_image': "https://www.tiendakrear3d.com/wp-content/uploads/2024/08/krear3dlogo.webp",
                'agency_id': 4,
                #'agency_id': row.agency_id,
                'status': row.status.name if row.status else None,
                'status_id': row.status.id if row.status else None,
                'register_at': row.register_date.strftime("%d %B %Y %I:%M %p") if row.register_date else None
            })

        return data, 200


    @handle_exceptions
    def get_order(self, data):
        order_number = data.get("order_number")
        agency_id = data.get("agency_id")

        client_order, client_order_status = self.client_repository.get_client_order_by_number(order_number)
        if client_order_status != 200:
            return client_order, client_order_status
        
        if agency_id < 4:
            tracking_order, tracking_order_status = self.tracking_repository.get_tracking_order(client_order.id)
            if tracking_order_status != 200:
                return tracking_order, tracking_order_status
            
            order_history, order_history_status = self.tracking_repository.get_order_history(tracking_order.id)
            if order_history_status != 200:
                return order_history, order_history_status

            history_data = []
            for history in order_history:
                history_data.append({
                    #'status_id': history.status_id,
                    'status_name': history.status.name,
                    'register_at': history.register_at.strftime("%d-%m-%Y %I:%M %p"),
                })

            result = {
                'agency_name': tracking_order.agency.name,
                'agency_id': tracking_order.agency_id,
                'code1': tracking_order.code1,
                'code2': tracking_order.code2,
                'origin_agency': tracking_order.origin_agency,
                'destination_agency': tracking_order.destination_agency,
                'last_status_name': tracking_order.status.name,
                'last_status_id': tracking_order.status_id,
                'status_history': history_data
            }
            return result, 200
        
        logistic_order, logistic_order_status = self.logistic_repository.get_logistic_order(client_order.id)
        if logistic_order_status != 200:
            return logistic_order, logistic_order_status
        
        result = {
            'agency_name': "Krear 3D",
            'agency_id': 4,
            'origin_agency': "Lima",
            'destination_agency': logistic_order.district.name,
            'last_status_name': logistic_order.status.name,
            'last_status_id': logistic_order.status_id,
            #'status_history': history_data
        }
        return result, 200
    