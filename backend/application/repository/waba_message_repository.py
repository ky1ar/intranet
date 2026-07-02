from application.handlers import handle_db_exceptions
from application.db_models.waba_message_model import WabaMessage
from application.models import Clients
from application.utils import peru_time, format_name
from sqlalchemy import func
from flask import g


class WabaMessageRepository:

    @handle_db_exceptions
    def log_inbound(self, wa_id, contact_name, wamid, msg_type, content, waba_timestamp, media_url=None):
        # Evita duplicados si Meta reintenta el webhook (mismo wamid).
        if wamid:
            existing = (
                g.db_session.query(WabaMessage)
                .filter(WabaMessage.wamid == wamid, WabaMessage.direction == 'in')
                .first()
            )
            if existing:
                return existing, 200

        msg = WabaMessage(
            wa_id          = wa_id,
            contact_name   = contact_name,
            wamid          = wamid,
            direction      = 'in',
            msg_type       = msg_type,
            content        = content,
            media_url      = media_url,
            waba_timestamp = waba_timestamp,
            created_at     = peru_time().replace(tzinfo=None),
        )
        g.db_session.add(msg)
        g.db_session.commit()
        return msg, 200

    @handle_db_exceptions
    def get_conversations(self, limit=25, offset=0):
        # Last message per wa_id
        last_ids = (
            g.db_session.query(func.max(WabaMessage.id))
            .group_by(WabaMessage.wa_id)
        )
        last_msgs = (
            g.db_session.query(WabaMessage)
            .filter(WabaMessage.id.in_(last_ids))
            .order_by(WabaMessage.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

        if not last_msgs:
            return [], 200

        wa_ids = [m.wa_id for m in last_msgs]

        # Mensajes entrantes sin leer por wa_id
        unread_rows = (
            g.db_session.query(WabaMessage.wa_id, func.count(WabaMessage.id))
            .filter(
                WabaMessage.wa_id.in_(wa_ids),
                WabaMessage.direction == 'in',
                WabaMessage.is_read.is_(False),
            )
            .group_by(WabaMessage.wa_id)
            .all()
        )
        unread_map = {row[0]: row[1] for row in unread_rows}

        # Most recent known contact_name per wa_id (from any inbound message)
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

        # For wa_ids still without a name, look up in clients by phone (stored as "51XXXXXXXXX")
        unnamed = [m.wa_id for m in last_msgs if m.wa_id not in name_map]
        if unnamed:
            clients = (
                g.db_session.query(Clients.phone, Clients.name)
                .filter(Clients.phone.in_(unnamed))
                .all()
            )
            for c in clients:
                if c.name:
                    name_map[c.phone] = c.name.title()

        # Last fallback: name captured from outbound templates (param 'name'/'username')
        still_unnamed = [m.wa_id for m in last_msgs if m.wa_id not in name_map]
        if still_unnamed:
            out_rows = (
                g.db_session.query(WabaMessage.wa_id, WabaMessage.contact_name)
                .filter(
                    WabaMessage.wa_id.in_(still_unnamed),
                    WabaMessage.direction == 'out',
                    WabaMessage.contact_name.isnot(None),
                )
                .order_by(WabaMessage.id.desc())
                .all()
            )
            for row in out_rows:
                if row.wa_id not in name_map and row.contact_name:
                    name_map[row.wa_id] = row.contact_name

        return [
            {
                "wa_id":         m.wa_id,
                "contact_name":  name_map.get(m.wa_id) or m.wa_id,
                "direction":     m.direction,
                "msg_type":      m.msg_type,
                "content":       m.content,
                "template_name": m.template_name,
                "unread_count":  unread_map.get(m.wa_id, 0),
                "created_at":    m.created_at.isoformat() if m.created_at else None,
            }
            for m in last_msgs
        ], 200

    @handle_db_exceptions
    def get_messages(self, wa_id, limit=200):
        # Al abrir el chat, marcamos como leidos los entrantes de esta conversacion
        updated = (
            g.db_session.query(WabaMessage)
            .filter(
                WabaMessage.wa_id == wa_id,
                WabaMessage.direction == 'in',
                WabaMessage.is_read.is_(False),
            )
            .update({WabaMessage.is_read: True}, synchronize_session=False)
        )
        if updated:
            g.db_session.commit()

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
            d["agent_name"] = format_name(row.agent.name, simple=True) if row.agent else None
            result.append(d)
        return result, 200
