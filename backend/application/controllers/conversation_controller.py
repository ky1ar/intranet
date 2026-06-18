from application.handlers import handle_logs_and_exceptions, validate_request
from application.services.conversation_service import ConversationService


class ConversationController:
    def __init__(self):
        self.service = ConversationService()

    @handle_logs_and_exceptions
    def get_conversations(self, data):
        return self.service.get_conversations(
            data.get("limit", 25),
            data.get("offset", 0),
        )

    @handle_logs_and_exceptions
    def get_messages(self, data):
        if validation := validate_request(data, {"wa_id"}):
            return validation, 400
        return self.service.get_messages(data["wa_id"])

    @handle_logs_and_exceptions
    def send_reply(self, data):
        if validation := validate_request(data, {"wa_id", "text"}):
            return validation, 400
        return self.service.send_reply(data["wa_id"], data["text"])
