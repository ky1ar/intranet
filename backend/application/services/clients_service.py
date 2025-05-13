import logging, colorsys, random, json
from application import redis_client
from application.handlers import handle_exceptions
from application.repository.user_repository import UserRepository
from application.repository.client_repository import ClientRepository
from application.proxy.apiperu import ApiPeru


class ClientsService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.client_repository = ClientRepository()
        self.apiperu = ApiPeru()

    
    @handle_exceptions
    def get_data(self, document):
        #if len(document) not in (8, 11):
        #    return 'Documento inválido', 400
        
        key = f"client_data:{document}"
        cache = redis_client.get(key)
        #if cache:
        #    logging.info('User data loaded from cache')
        #    return json.loads(cache), 200
        
        user_data, user_status = self.client_repository.get_client_by_document(document)
        if user_status == 500:
            return user_data, user_status
        
        if user_status == 200:
            user_dict = user_data.to_dict(only_fields=['id', 'document', 'name', 'phone', 'email'])
            if 'phone' in user_dict and user_dict['phone']:
                user_dict['phone'] = user_dict['phone'][2:]

            redis_client.set(key, json.dumps(user_dict))
            return user_dict, 200
        
        if len(document) == 8:
            return self.apiperu.get_name('dni', document)
        
        if len(document) == 11:
            return self.apiperu.get_name('ruc', document)
        
        return "Datos de usuario no encontrados", 404

        
    @handle_exceptions
    def get_name(self, document):
        if len(document) not in (8, 11):
            return "Nombre de usuario no encontrado", 404
        
        if len(document) == 8:
            return self.apiperu.get_name('dni', document)
        
        return self.apiperu.get_name('ruc', document)


    @handle_exceptions
    def generate_matte_hex_color(self):
        h = random.random()
        s = random.uniform(0.15, 0.3)
        l = random.uniform(0.6, 0.6)
        r, g, b = colorsys.hls_to_rgb(h, l, s)

        return '#{:02x}{:02x}{:02x}'.format(int(r*255), int(g*255), int(b*255))
    

    @handle_exceptions
    def clients_all(self, data):
        page = data.get("page")
        per_page = data.get("per_page")
        result, status = self.user_repository.get_all_clients(page=page, per_page=per_page)
        if status != 200:
            return result, status
        
        clients_list = []
        for client in result["clients"]:
            client_data = {
                "id": client.id,
                "name": client.name.title(),
                "color": self.generate_matte_hex_color(),
                "letter": client.name[0].title(),
                "document": client.document,
                "email": client.email,
                "phone": client.phone,
            }
            clients_list.append(client_data)

        return {
            "clients": clients_list,
            "pagination": {
                "total": result["total"],
                "page": result["page"],
                "per_page": result["per_page"],
                "pages": result["pages"],
            }
        }, 200
    

    @handle_exceptions
    def get_user_order(self, order_number):
        #key = f"client_data:{document}"
        #cache = redis_client.get(key)
        #if cache:
        #    logging.info('User data loaded from cache')
        #    return json.loads(cache), 200
        client_order, client_order_status = self.client_repository.get_client_order_by_number(order_number)
        if client_order_status != 200:
            return client_order, client_order_status

        result = {
            "client_order_id": client_order.id,
            "client": {
                "document": client_order.client.document,
                "id": client_order.client_id,
                "name": client_order.client.name.title(),
                "email": client_order.client.email,
                "phone": client_order.client.phone[2:],
            }
        }

        #redis_client.set(key, json.dumps(user_dict))
        return result, 200