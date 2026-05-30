from application.handlers import handle_db_exceptions
from application.db_models.waba_message_model import WabaMessage
from sqlalchemy import func
from flask import g


class WabaMessageRepository:

    @handle_db_exceptions
    def log_inbound(self, wa_id, contact_name, wamid, msg_type, content, waba_timestamp):
        msg = WabaMessage(
            wa_id          = wa_id,
            contact_name   = contact_name,
            wamid          = wamid,
            direction      = 'in',
            msg_type       = msg_type,
            content        = content,
            waba_timestamp = waba_timestamp,
        )
        g.db_session.add(msg)
        g.db_session.commit()
        return msg, 200

    @handle_db_exceptions
    def get_conversations(self):
        # Last message per wa_id
        last_ids = (
            g.db_session.query(func.max(WabaMessage.id))
            .group_by(WabaMessage.wa_id)
        )
        last_msgs = (
            g.db_session.query(WabaMessage)
            .filter(WabaMessage.id.in_(last_ids))
            .order_by(WabaMessage.created_at.desc())
            .all()
        )

        if not last_msgs:
            return [], 200

        # Most recent known contact_name per wa_id (from any inbound message)
        wa_ids = [m.wa_id for m in last_msgs]
        name_rows = (
            g.db_session.query(WabaMessage.wa_id, WabaMessage.contact_name)
            .filter(
                WabaMessage.wa_id.in_(wa_ids),
                WabaMessage.direction == 'in',
                WabaMessage.contact_name.isnot(None),
            )
            .order_by(WabaMessage.id.desc())
            .all()
        )
        name_map = {}
        for row in name_rows:
            if row.wa_id not in name_map:
                name_map[row.wa_id] = row.contact_name

        return [
            {
                "wa_id":         m.wa_id,
                "contact_name":  name_map.get(m.wa_id, m.wa_id),
                "direction":     m.direction,
                "msg_type":      m.msg_type,
                "content":       m.content,
                "template_name": m.template_name,
                "created_at":    m.created_at.isoformat() if m.created_at else None,
            }
            for m in last_msgs
        ], 200

    @handle_db_exceptions
    def get_messages(self, wa_id, limit=200):
        rows = (
            g.db_session.query(WabaMessage)
            .filter(WabaMessage.wa_id == wa_id)
            .order_by(WabaMessage.created_at.asc())
            .limit(limit)
            .all()
        )
        result = []
        for row in rows:
            d = row.to_dict()
            d["created_at"] = row.created_at.isoformat() if row.created_at else None
            result.append(d)
        return result, 200
