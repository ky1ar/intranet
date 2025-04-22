import logging

from datetime import date, datetime, timezone, timedelta
from application.handlers import handle_exceptions
from application.repository.tracking_repository import TrackingRepository
from application.repository.user_repository import UserRepository
from application.proxy.shalom import Shalom
from application.proxy.olva import Olva
from application.proxy.marvisur import Marvisur


class TrackingService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.tracking_repository = TrackingRepository()
        self.shalom = Shalom()
        self.olva = Olva()
        self.marvisur = Marvisur()


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
                
                client, client_status = self.user_repository.get_user_by_document(document)
                if client_status == 200:
                    client_id = client.id
                else:
                    added_client, added_client_status = self.user_repository.add_client(client_data)
                    if added_client_status != 200:
                        return added_client, added_client_status
                    client_id = added_client
            
            user_order, user_status = self.user_repository.add_user_order(order_number, client_id)
            if user_status != 200:
                return user_order, user_status
            data["user_order_id"] = user_order

        else:
            _, find_status = self.tracking_repository.get_tracking_order(user_order_id)
            if find_status == 200:
                return "La Orden ya ha sido registrada", 400
        
        if agency_id == '1':
            shalom_track, shalom_status = self.shalom.tracking(code1, code2)
            if shalom_status != 200:
                return shalom_track, shalom_status
            
            if shalom_track.get('success') == False:
                return "Tracking no encontrado", 400
            
            shalom_data = shalom_track.get('data')
            shalom_origin = shalom_data.get('origen')
            shalom_destination = shalom_data.get('destino')

            data['origin_agency'] = f"{shalom_origin.get('nombre')}, {shalom_origin.get('departamento')}".title()
            data['destination_agency'] = f"{shalom_destination.get('nombre')}, {shalom_destination.get('departamento')}".title()
            data['external_id'] = shalom_data.get('ose_id')

        elif agency_id == '2':
            olva_track, olva_status = self.olva.tracking(code1, code2)
            if olva_status == 502:
                return olva_track, olva_status
            
            if olva_status == 404:
                return "Tracking no encontrado", 400
            
            olva_data = olva_track.get('data').get('general')
            data['origin_agency'] = f"{olva_data.get('origen')}".title()
            data['destination_agency'] = f"{olva_data.get('destino')}".title()

        elif agency_id == '3':
            marvisur_track, marvisur_status = self.marvisur.tracking(code1, code2)
            if marvisur_status != 200:
                return marvisur_track, marvisur_status
            
            if marvisur_track.get('success') == False:
                return "Tracking no encontrado", 400
            
            marvisur_data = marvisur_track.get('data').get('Table')
            for item in marvisur_data:
                if item.get('COMENTARIO') == "RECEPCION":
                    data['origin_agency'] = item.get('DEPORIGEN', '').title()
                    data['destination_agency'] = item.get('DEPDESTINO', '').title()
                    break
                
        tracking_order, tracking_status = self.tracking_repository.add_tracking_order(data)
        if tracking_status != 200:
            return tracking_order, tracking_status
        
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
                'order_number': track.user_order.number,
                'agency': track.agency.name if track.agency else None,
                'agency_id': track.agency_id,
                'status': track.status.name if track.status else None,
                'code1': track.code1,
                'code2': track.code2,
                'register_at': track.register_at.isoformat() if track.register_at else None
            })

        return data, 200