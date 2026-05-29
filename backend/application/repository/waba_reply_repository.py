from application.handlers import handle_db_exceptions
from application.db_models.waba_reply_model import WabaReply
from flask import g


class WabaReplyRepository:

    @handle_db_exceptions
    def save(self, wa_id, msg_type, content=None, contact_name=None,
             wamid=None, conversation_id=None, origin_type=None, waba_timestamp=None):
        reply = WabaReply(
            wa_id           = wa_id,
            contact_name    = contact_name,
            wamid           = wamid,
            msg_type        = msg_type,
            content         = content,
            conversation_id = conversation_id,
            origin_type     = origin_type,
            waba_timestamp  = waba_timestamp,
        )
        g.db_session.add(reply)
        g.db_session.commit()
        return reply, 200
