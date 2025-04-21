import logging, colorsys, random
from application import bcrypt, redis_client
from application.handlers import handle_exceptions
from application.repository.user_repository import UserRepository


class ClientsService:
    def __init__(self):
        self.user = UserRepository()
        

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
        result, status = self.user.get_all_clients(page=page, per_page=per_page)
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