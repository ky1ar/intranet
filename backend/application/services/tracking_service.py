import logging

from datetime import date, datetime, timezone, timedelta
from application.handlers import handle_exceptions
from application.repository.tracking_repository import TrackingRepository
from application.repository.user_repository import UserRepository


class TrackingService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.tracking_repository = TrackingRepository()


    @handle_exceptions
    def add(self, data):
        user_order_id = data.get("user_order_id")
        order_number = data.get("order_number", "").strip()
        agency_id = data.get("agency_id")
        code1 = data.get("code1")
        code2 = data.get("code2")

        if not agency_id:
            return "Seleccione una agencia", 400
        if not code1:
            return "Ingrese el código 1", 400
        if not code2:
            return "Ingrese el código 2", 400
        
        if not user_order_id:
            logging.info("Not user_order_id find, creating new one")
            if not order_number:
                return "Ingrese el número de orden", 400
            
            client_id = data.get("client_id")
            client_data = data.pop("client")

            document = client_data.get("document", "").strip()
            name = client_data.get("name", "").strip()
            phone = client_data.get("phone", "").strip()

            if not phone or len(phone) != 9:
                return "Ingrese un celular válido", 400
        
            if client_id:
                logging.info("client_id already exist")
                client, client_status = self.user_repository.get_user_by_id(client_id)
                if client_status != 200:
                    return client, client_status
                self.user_repository.update_client(client, client_data)
            else:
                logging.info("Client not exist, creating new one")
                if not document:
                    return "Ingrese un documento", 400
                if not name:
                    return "Ingrese el nombre", 400
                
                added_client, added_client_status = self.user_repository.add_client(client_data)
                if added_client_status != 200:
                    return added_client, added_client_status
                client_id = added_client
            
            user_order, user_order_status = self.user_repository.add_user_order(order_number, client_id)
            if user_order_status != 200:
                return user_order, user_order_status
            data["user_order_id"] = user_order

        tracking_order, tracking_order_status = self.tracking_repository.add_tracking_order(data)
        if tracking_order_status != 200:
            return tracking_order, tracking_order_status
        
        #socketio.emit("update_schedule", {})
        return "Orden registrada correctamente", 200
        


    @handle_exceptions
    def list(self, document):
        client, client_status = self.user_repository.get_user_by_document(document)
        if client_status != 200:
            return client, client_status
        
        orders, orders_status = self.user_repository.get_user_orders(client.id)
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
                #'order_number': track.user_order.number,
                'agency': track.agency.name if track.agency else None,
                #'status': track.status.name if track.status else None,
                'code1': track.code1,
                'code2': track.code2,
                #'register_at': track.register_at.isoformat() if track.register_at else None
            })

        return data, 200