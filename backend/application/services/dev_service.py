import logging, time, hmac, hashlib, uuid
from application.repository.dev_repository import DevRepository
from application.repository.waba_reply_repository import WabaReplyRepository
from application.repository.waba_message_repository import WabaMessageRepository
from application.handlers import handle_exceptions
from application.proxy.whatsapp import Whatsapp
from application.services.push_service import PushSender
from application.repository.user_repository import UserRepository
from flask import g


class DevService:
    NOTIFY_USER_ID = 23

    def __init__(self):
        self.dev_repository = DevRepository()
        self.waba_reply_repository = WabaReplyRepository()
        self.waba_message_repository = WabaMessageRepository()
        self.user_repository = UserRepository()
        self.whatsapp = Whatsapp()
        self.push_service = PushSender()
        self.default_campaign = 'shining_event'


    @handle_exceptions
    def extract_data(self, payload):
        entry = payload.get("entry", [])[0]
        change = entry.get("changes", [])[0]
        value = change.get("value", {})

        contacts = value.get("contacts", [])
        wa_id = contacts[0].get("wa_id") if contacts else None

        messages = value.get("messages", [])
        message_text = messages[0].get("text", {}).get("body") if messages else None

        if not wa_id or not message_text:
            return "Missing 'wa_id' or 'message'", 400
        
        return {
            "phone": wa_id,
            "message": message_text
        }, 200
    

    def _extract_content(self, msg_type, message):
        if msg_type == "text":
            return message.get("text", {}).get("body")
        if msg_type == "reaction":
            return message.get("reaction", {}).get("emoji")
        if msg_type == "button":
            return message.get("button", {}).get("payload")
        if msg_type == "interactive":
            iv = message.get("interactive", {})
            reply = iv.get("button_reply") or iv.get("list_reply") or {}
            return reply.get("title") or reply.get("id")
        if msg_type == "image":
            return message.get("image", {}).get("caption")
        if msg_type == "audio":
            return "(audio)"
        if msg_type == "document":
            return message.get("document", {}).get("filename") or "(documento)"
        if msg_type == "video":
            return message.get("video", {}).get("caption") or "(video)"
        if msg_type == "location":
            loc = message.get("location", {})
            return f"{loc.get('latitude')},{loc.get('longitude')}"
        if msg_type == "sticker":
            return "(sticker)"
        return None

    @handle_exceptions
    def process_webhook(self, data):
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if not messages:
            #logging.info("Webhook ignorado: sin mensajes.")
            return "Sin mensajes", 200

        message  = messages[0]
        msg_type = message.get("type")
        wa_id    = message.get("from")
        wamid    = message.get("id")
        waba_ts  = int(message.get("timestamp", 0)) or None

        contacts = value.get("contacts", [])
        contact_name = (contacts[0].get("profile", {}).get("name") if contacts else None)

        conversation_id = None
        origin_type     = None
        # statuses block won't be here (messages path), but guard anyway
        for conv_src in [message.get("context", {}), {}]:
            pass
        # conversation comes from statuses, not messages; leave None for replies

        content = self._extract_content(msg_type, message)

        # Guardar en DB (en hilo separado no es necesario; el webhook responde rápido)
        try:
            self.waba_reply_repository.save(
                wa_id           = wa_id,
                msg_type        = msg_type,
                content         = content,
                contact_name    = contact_name,
                wamid           = wamid,
                conversation_id = conversation_id,
                origin_type     = origin_type,
                waba_timestamp  = waba_ts,
            )
        except Exception as e:
            logging.exception(f"[WabaReply] Error al guardar: {e}")

        try:
            self.waba_message_repository.log_inbound(
                wa_id          = wa_id,
                contact_name   = contact_name,
                wamid          = wamid,
                msg_type       = msg_type,
                content        = content,
                waba_timestamp = waba_ts,
            )
        except Exception as e:
            logging.exception(f"[WabaMessage] Error al guardar inbound: {e}")

        # Push a usuario 23
        try:
            display_name = contact_name or wa_id
            push_body = content or f"({msg_type})"
            self.push_service.send_to_user(
                user_id = self.NOTIFY_USER_ID,
                title   = f"WA · {display_name}",
                body    = push_body,
                data    = {"wa_id": wa_id, "type": msg_type},
            )
        except Exception as e:
            logging.exception(f"[WabaReply] Error al enviar push: {e}")

        # Flujo de botones de campaña (igual que antes)
        if msg_type != "button":
            logging.info(f"Webhook registrado: tipo {msg_type}.")
            return "Mensaje registrado", 200

        context_msg_id = message.get("context", {}).get("id", "")
        button_payload = message.get("button", {}).get("payload")

        if not wa_id or not context_msg_id or not button_payload:
            logging.warning("Faltan datos esenciales en el webhook.")
            return "Datos incompletos", 200

        user, user_status = self.dev_repository.get_user_by_phone(self.default_campaign, f"+{wa_id}")
        if user_status != 200:
            return user, user_status

        if context_msg_id == user.last_message_id:
            campaign_data = {"name": user.name, "phone": user.phone}
            if button_payload == "SÍ, asistiré":
                _, send_status = self.whatsapp.confirm_flow_yes(self.default_campaign, campaign_data)
                if send_status != 200:
                    return "Error al enviar el whatsapp", 400
                user_wsp, user_status = self.dev_repository.update_user(user, status='yes')
                if user_status != 200:
                    return user_wsp, user_status
                return "Mensaje enviado", 200

            elif button_payload == "NO podré asistir":
                _, send_status = self.whatsapp.confirm_flow_no(self.default_campaign, campaign_data)
                if send_status != 200:
                    return "Error al enviar el whatsapp", 400
                user_wsp, user_status = self.dev_repository.update_user(user, status='no')
                if user_status != 200:
                    return user_wsp, user_status
                return "Mensaje enviado", 200

        logging.info("Webhook de botón procesado sin acción (contexto no coincide o no relevante).")
        return "Botón procesado sin acción", 200
    

    @handle_exceptions
    def confirm_flow(self, phone):
        user, user_status = self.dev_repository.get_user_by_phone(phone)
        if user_status != 200:
            return user, user_status
        
        send_wsp, send_status = self.whatsapp.confirm_flow_start(phone)
        if send_status != 200:
            return "Error al enviar el whatsapp", 400

        last_message_id = send_wsp["messages"][0]["id"]
        user_wsp, user_status = self.dev_repository.update_user(user, last_message_id)
        if user_status != 200:
            return user_wsp, user_status

        return "Mensaje enviado", 200


    @handle_exceptions
    def confirm_flow_all(self, campaign):
        users, uc = self.dev_repository.get_all_pending_users(campaign)
        if uc != 200:
            return users, uc
        
        results = []
        for user in users:
            data = {
                "phone": user.phone,
                "name": user.name
            }

            try:
                send, sc = self.whatsapp.confirm_flow_start(campaign, data)
                if sc != 200:
                    results.append({"phone": data.get("phone"), "status": "error", "error": send})
                    continue

                last_message_id = send["messages"][0]["id"]
                _, update_status = self.dev_repository.update_user(user, last_message_id)
                results.append({"phone": data.get("phone"), "status": "ok" if update_status == 200 else "update_error"})

                time.sleep(1.5)
            except Exception as e:
                results.append({"phone": data.get("phone"), "status": "exception", "error": str(e)})

        return "Mensajes enviados correctamente", 200


    @handle_exceptions
    def confirm_flow_list(self, campaign):
        users, uc = self.dev_repository.get_all_users(campaign)
        if uc != 200:
            return users, uc

        # accepted, ac = self.dev_repository.count_accepted_users()
        # if ac != 200:
        #     return accepted, ac

        return {
            "total_users": len(users),
            # "accepted": accepted,
            "users": [u.to_dict(only_fields=["id", "name", "phone", "status", "sended_at", "updated_at"]) for u in users]
        }, 200


    @handle_exceptions
    def confirm_flow_reminder(self):
        users, status = self.dev_repository.get_accepted_users()
        if status != 200:
            return users, status
        
        results = []
        for user in users:
            phone = user.phone
            try:
                send_wsp, send_status = self.whatsapp.confirm_flow_reminder(phone)
                if send_status != 200:
                    results.append({"phone": phone, "status": "error", "error": send_wsp})
                    continue
                
                _, user_status = self.dev_repository.update_user(user, status='reminded')
                results.append({"phone": phone, "status": "ok" if user_status == 200 else "update_error"})

                time.sleep(1.5)

            except Exception as e:
                results.append({"phone": phone, "status": "exception", "error": str(e)})

        return "Recordatorios enviados correctamente", 200
    

    @handle_exceptions
    def confirm_flow_reminder_2(self):
        users, status = self.dev_repository.get_confirmed_users()
        if status != 200:
            return users, status
        
        results = []
        for user in users:
            phone = user.phone
            try:
                send_wsp, send_status = self.whatsapp.confirm_flow_reminder_2(phone)
                if send_status != 200:
                    results.append({"phone": phone, "status": "error", "error": send_wsp})
                    continue
                
                _, user_status = self.dev_repository.update_user(user, status='reminded')
                results.append({"phone": phone, "status": "ok" if user_status == 200 else "update_error"})

                time.sleep(1.5)

            except Exception as e:
                results.append({"phone": phone, "status": "exception", "error": str(e)})

        return "Recordatorios enviados correctamente", 200
    

    @handle_exceptions
    def mkt_campaign(self, data):
        template_name = data.get("template_name")
        phones = data.get("phones")
        parameters = data.get("parameters")
        header_image = data.get("header_image")

        results = []
        for phone in phones:
            waba_phone = f"51{phone}" if not str(phone).startswith("51") else str(phone)
            try:
                _, status = self.whatsapp.mkt_campaign(waba_phone, template_name, header_image, parameters)
                results.append({"phone": phone, "status": "ok" if status == 200 else "error"})
                time.sleep(1.5)
            except Exception as e:
                results.append({"phone": phone, "status": "exception", "error": str(e)})

        sent = sum(1 for r in results if r["status"] == "ok")
        return {"sent": sent, "total": len(phones), "results": results}, 200


    @handle_exceptions
    def token(self):
        secret = b".Ov3rsku112024l4r43l."
        u = str(uuid.uuid4())
        exp = int(time.time()) + 30

        base = f"web-{u}@{exp}"
        sig = hmac.new(secret, base.encode("utf-8"), hashlib.sha256).hexdigest()

        return f"{base}@{sig}", 200
    

    @handle_exceptions
    def push(self, data):
        pn_title = data.get("title")
        message = data.get("message")

        user_ids, duic = self.user_repository.get_all_user_ids()
        if duic != 200:
            return user_ids, duic
        
        self.push_service.send_to_users(
            user_ids=user_ids,
            title=pn_title,
            body=message,
        )

        return "Enviado correctamente", 200
