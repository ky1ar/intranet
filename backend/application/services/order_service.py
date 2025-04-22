import logging

from datetime import date, datetime, timezone, timedelta
from application.handlers import handle_exceptions
from application.repository.user_repository import UserRepository


class OrderService:
    def __init__(self):
        self.user_repository = UserRepository()


    @handle_exceptions
    def get_user_order(self, order_number):
        #key = f"client_data:{document}"
        #cache = redis_client.get(key)
        #if cache:
        #    logging.info('User data loaded from cache')
        #    return json.loads(cache), 200
        user_order, user_order_status = self.user_repository.get_user_order_by_number(order_number)
        if user_order_status != 200:
            return user_order, user_order_status

        result = {
            "user_order_id": user_order.id,
            "client": {
                "document": user_order.client.document,
                "id": user_order.client_id,
                "name": user_order.client.name.title(),
                "phone": user_order.client.phone[2:],
            }
        }

        #redis_client.set(key, json.dumps(user_dict))
        return result, 200
    