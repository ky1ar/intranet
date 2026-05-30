from application.handlers import handle_exceptions
from application.repository.waba_message_repository import WabaMessageRepository
from application.proxy.whatsapp import Whatsapp


class ConversationService:
    def __init__(self):
        self.repository = WabaMessageRepository()
        self.whatsapp   = Whatsapp()

    @handle_exceptions
    def get_conversations(self):
        return self.repository.get_conversations()

    @handle_exceptions
    def get_messages(self, wa_id):
        return self.repository.get_messages(wa_id)

    @handle_exceptions
    def send_reply(self, wa_id, text):
        result, status = self.whatsapp.send_text(wa_id, text.strip())
        if status != 200:
            return "Error sending message", 400
        return "Message sent", 200
