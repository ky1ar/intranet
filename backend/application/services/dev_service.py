import logging, time
from application.repository.dev_repository import DevRepository
from application.handlers import handle_exceptions, handle_db_exceptions
from application.proxy.whatsapp import Whatsapp
from flask import g


class DevService:
    def __init__(self):
        self.dev_repository = DevRepository()
        self.whatsapp = Whatsapp()
        self.default_campaign = 'creality_fest'


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
    

    @handle_exceptions
    def process_webhook(self, data):
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        
        if not messages:
            logging.info("Webhook ignorado: sin mensajes.")
            return "Sin mensajes", 200

        msg_type = messages[0].get("type")
        if msg_type != "button":
            logging.info(f"Webhook ignorado: tipo {msg_type} no manejado.")
            return "Tipo de mensaje ignorado", 200

        message = messages[0]
        user_wa_id = message.get("from")
        context_msg_id = message.get("context", {}).get("id")
        button_payload = message.get("button", {}).get("payload")

        if not user_wa_id or not context_msg_id or not button_payload:
            logging.warning("Faltan datos esenciales en el webhook.")
            return "Datos incompletos", 200

        user, user_status = self.dev_repository.get_user_by_phone(f"+{user_wa_id}")
        if user_status != 200:
            return user, user_status
        
        # 🔍 Comparación tolerante del mensaje de contexto
        if user.last_message_id and context_msg_id and context_msg_id in user.last_message_id:
            if user.campaign == self.default_campaign:
                if button_payload == "Sí, asistiré":
                    _, send_status = self.whatsapp.confirm_flow_yes(f"+{user_wa_id}")
                    if send_status != 200:
                        return "Error al enviar el whatsapp", 400

                    user_wsp, user_status = self.dev_repository.update_user(user, status='accepted')
                    if user_status != 200:
                        return user_wsp, user_status
                    return "Mensaje enviado", 200

                elif button_payload == "No podré asistir":
                    _, send_status = self.whatsapp.confirm_flow_no(f"+{user_wa_id}")
                    if send_status != 200:
                        return "Error al enviar el whatsapp", 400

                    user_wsp, user_status = self.dev_repository.update_user(user, status='declined')
                    if user_status != 200:
                        return user_wsp, user_status
                    return "Mensaje enviado", 200

        # ⚠️ Si el contexto no coincide, no disparamos respuesta
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
    def confirm_flow_all(self):
        users, status = self.dev_repository.get_all_pending_users()
        if status != 200:
            return users, status
        
        results = []
        for user in users:
            phone = user.phone
            try:
                send_wsp, send_status = self.whatsapp.confirm_flow_start(phone)
                if send_status != 200:
                    results.append({"phone": phone, "status": "error", "error": send_wsp})
                    continue

                last_message_id = send_wsp["messages"][0]["id"]
                _, update_status = self.dev_repository.update_user(user, last_message_id)
                results.append({"phone": phone, "status": "ok" if update_status == 200 else "update_error"})

                time.sleep(1.5)
            except Exception as e:
                results.append({"phone": phone, "status": "exception", "error": str(e)})

        return "Mensajes enviados correctamente", 200


    @handle_exceptions
    def confirm_flow_list(self):
        all_users, status = self.dev_repository.get_all_users()
        if status != 200:
            return all_users, status

        total_accepted, accepted_status = self.dev_repository.count_accepted_users()
        if accepted_status != 200:
            return total_accepted, accepted_status

        return {
            "total_users": total_accepted,
            #"total_users": len(all_users),
            "total_accepted": total_accepted,
            "users": [u.to_dict(only_fields=["id", "name", "phone", "status", "sended_at", "updated_at"]) for u in all_users]
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