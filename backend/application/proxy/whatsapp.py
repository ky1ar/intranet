import logging, requests, json
from datetime import datetime
from application.handlers import handle_exceptions
from config import WABA as API
from config import Config
from config import Odoo


class Whatsapp:
    def __init__(self):
        self.token = API.TOKEN
        self.whatsapp_url = API.URL
        
        self.image_base_url = Config.BASE_URL
        self.pdf_base_url = Odoo.PDF_URL

        self.review_url = Config.REVIEW_URL
        self.mantra_phone = Config.CONTACT_PHONE

        self.support_terms = Config.SUPPORT_TERMS
        self.support_phone = Config.SUPPORT_CONTACT_PHONE
        self.support_url = "https://soporte.krear3d.com/consultas"

        self.tracking_url = "http://tiendakrear3d.com/rastrear-pedidos"


    dias_semana = {
        0: 'lunes',
        1: 'martes',
        2: 'miércoles',
        3: 'jueves',
        4: 'viernes',
        5: 'sábado',
        6: 'domingo'
    }

    meses = {
        1: 'enero',
        2: 'febrero',
        3: 'marzo',
        4: 'abril',
        5: 'mayo',
        6: 'junio',
        7: 'julio',
        8: 'agosto',
        9: 'septiembre',
        10: 'octubre',
        11: 'noviembre',
        12: 'diciembre'
    }


    def to_waba_phone(pe_9_digits: str) -> str:
        return f"51{pe_9_digits}"


    def post(self, payload):
        logging.info(payload)
        url = f"{self.whatsapp_url}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response_data = response.json()
        if response.status_code != 200:
            logging.info(response.text)
            return f"Error {response_data}", response.status_code

        logging.info(response_data)
        self._log_outbound(payload)
        return response_data, 200


    def _log_outbound(self, payload):
        try:
            from application import app, db
            from sqlalchemy import text as sa_text
            import time as _time

            to        = payload.get("to", "")
            msg_type  = payload.get("type", "")
            content   = None
            tmpl_name = None

            if msg_type == "template":
                tmpl      = payload.get("template", {})
                tmpl_name = tmpl.get("name")
                for comp in tmpl.get("components", []):
                    if comp.get("type") == "body":
                        params  = [p.get("text", "") for p in comp.get("parameters", []) if p.get("type") == "text"]
                        content = " | ".join(filter(None, params)) or None
                        break
            elif msg_type == "text":
                content = payload.get("text", {}).get("body")

            with app.app_context():
                with db.engine.connect() as conn:
                    conn.execute(
                        sa_text(
                            "INSERT INTO waba_message "
                            "(wa_id, direction, msg_type, content, template_name, waba_timestamp, created_at) "
                            "VALUES (:wa_id, 'out', :msg_type, :content, :tmpl_name, :ts, NOW())"
                        ),
                        {"wa_id": to, "msg_type": msg_type, "content": content,
                         "tmpl_name": tmpl_name, "ts": int(_time.time())}
                    )
                    conn.commit()
        except Exception as e:
            logging.exception(f"[WabaMessage] Log outbound failed: {e}")


    @handle_exceptions
    def send_text(self, phone, text):
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "text",
            "text": {"body": text},
        }
        return self.post(payload)
    

    @handle_exceptions
    def tracking_alert(self, data):
        agency_id = data.get("agency_id")
        code1 = None
        code2 = None
        code3 = None


        if agency_id == 1: # Shalom
            code1 = f"N° de Orden Shalom: *{data.get('code1')}*"
            code2 = f"Código: *{data.get('code2')}*"
            code3 = f"Clave de recojo: *{data.get('code3')}*"
    
        elif agency_id == 2: # Olva
            code1 = f"N° de Tracking: *{data.get('code1')}*"
            code2 = f"Año: *{data.get('code2')}*"
            code3 = ""

        else: # Marvisur
            code1 = f"Serie: *{data.get('code1')}*"
            code2 = f"Número: *{data.get('code2')}*"
            code3 = ""

        parameters = [
            {"type": "text", "parameter_name": "username", "text": data.get("client_name")},
            {"type": "text", "parameter_name": "order", "text": data.get("order_number")},
            {"type": "text", "parameter_name": "agency", "text": data.get("agency")},
            {"type": "text", "parameter_name": "code1", "text": code1},
            {"type": "text", "parameter_name": "code2", "text": code2},
            {"type": "text", "parameter_name": "code3", "text": code3},
            {"type": "text", "parameter_name": "url", "text": self.tracking_url},
        ]

        payload = {
            "messaging_product": "whatsapp",
            "to": data.get("phone"),
            "type": "template",
            "template": {
                "name": "tracking_alert",
                "language": {"code": "es_PE"},
                "components": [{"type": "body", "parameters": parameters}]
            }
        }
        return self.post(payload)
    

    @handle_exceptions
    def otp(self, phone, otp_code):
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "template",
            "template": {
                "name": "krear3dotp",
                "language": {"code": "es_PE"},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {
                                "type": "text",
                                "text": otp_code
                            }
                        ]
                    },
                    {
                        "type": "button",
                        "sub_type": "url",
                        "index": 0,
                        "parameters": [
                            {
                                "type": "text",
                                "text": otp_code 
                            }
                        ]
                    }
                ]
            }
        }
        return self.post(payload)
    

    @handle_exceptions
    def new_order(self, phone, notes, order_number, machine_name):
        clean_notes = (notes or "").replace("\n", " ").replace("\t", " ").strip()
        clean_notes = ' '.join(clean_notes.split())

        parameters = [
            #{"type": "text", "parameter_name": "username", "text": client_name},
            {"type": "text", "parameter_name": "device_model", "text": machine_name},
            {"type": "text", "parameter_name": "order_number", "text": order_number},
            {"type": "text", "parameter_name": "url", "text": self.support_url},
        ]

        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "template",
            "template": {
                "name": "soporte_0_registro",
                "language": {"code": "es_PE"},
                "components": [{"type": "body", "parameters": parameters}]
            }
        }
        return self.post(payload)
    

    @handle_exceptions
    def new_order_alert(self, phone, order_number, machine_name):
        parameters = [
            {"type": "text", "parameter_name": "order_number", "text": order_number},
            {"type": "text", "parameter_name": "device_model", "text": machine_name},
        ]

        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "template",
            "template": {
                "name": "soporte_0_alert",
                "language": {"code": "es_PE"},
                "components": [{"type": "body", "parameters": parameters}]
            }
        }
        return self.post(payload)
    

    @handle_exceptions
    def status_change(self, current_status_id, client_phone, client_name, machine_name, filename=None):
        templates = {
            1: "soporte_0_ingreso",
            2: "soporte_1_revision",
            3: "soporte_2_diagnostico",
            4: "soporte_3_repuesto",
            5: "soporte_4_reparacion",
            6: "soporte_5_pruebas",
            7: "soporte_6_recojo",
            8: "soporte_7_entrega",
        }
                
        parameters = [
            {"type": "text", "parameter_name": "username", "text": client_name},
        ]

        if current_status_id == 1:
            parameters.append({
                "type": "text", 
                "parameter_name": "machine", 
                "text": machine_name
            })
            parameters.append({
                "type": "text", 
                "parameter_name": "notes", 
                "text": "🛠️"
            })
            parameters.append({
                "type": "text", 
                "parameter_name": "terms_link", 
                "text": self.support_terms
            })

        if current_status_id == 3:
            parameters.append({
                "type": "text", 
                "parameter_name": "number", 
                "text": self.support_phone
            })

        if current_status_id == 8:
            parameters.append({
                "type": "text", 
                "parameter_name": "link", 
                "text": self.review_url
            })

        payload = {
            "messaging_product": "whatsapp",
            "to": client_phone,
            "type": "template",
            "template": {
                "name": templates.get(current_status_id),
                "language": {"code": "es_PE"},
                "components": [{"type": "body", "parameters": parameters}]
            }
        }

        if current_status_id == 8:
            header_component = {
                "type": "header",
                "parameters": [
                    {
                        "type": "image",
                        "image": {
                            "link": f"{self.image_base_url}{filename}"
                        }
                    }
                ]
            }
            payload["template"]["components"].insert(0, header_component)
        return self.post(payload)
    

    @handle_exceptions
    def logistic_status_change(self, data, status_id):
        phone = data.get("phone")
        username = data.get("username")
        order_number = data.get("order_number")
        schedule_id = data.get("schedule_id")
        delivery_date = data.get("delivery_date")
        file = data.get("file")

        template_list = {
            2: "logistica_agendado",
            3: "entrega",
            4: "entrega_exitosa_img",
            6: "no_entrega_img",
        }

        template_name = template_list.get(status_id)
        schedules = {
            1: (Config.T1_START, Config.T1_END),
            2: (Config.T2_START, Config.T2_END)
        }
        start, end = schedules.get(schedule_id)
        timer = 10

        parameters = [{"type": "text", "parameter_name": "username", "text": username}]

        if status_id == 2:
            fecha_obj = datetime.strptime(delivery_date, "%Y-%m-%d")
            dia_semana = self.dias_semana[fecha_obj.weekday()]
            mes = self.meses[fecha_obj.month]
            dia = fecha_obj.day
            parameters.extend([
                {"type": "text", "parameter_name": "order_number", "text": order_number},
                {"type": "text", "parameter_name": "delivery_date", "text": f"{dia_semana} {dia} de {mes}"},
            ])
        elif status_id == 3:
            parameters.extend([
                {"type": "text", "parameter_name": "order_number", "text": order_number},
                {"type": "text", "parameter_name": "start", "text": start},
                {"type": "text", "parameter_name": "end", "text": end},
                {"type": "text", "parameter_name": "timer", "text": timer}
            ])
        elif status_id == 4:
            parameters.extend([
                {"type": "text", "parameter_name": "number", "text": self.mantra_phone},
                {"type": "text", "parameter_name": "link", "text": self.review_url}
            ])
        elif status_id == 6:
            parameters.append({"type": "text", "parameter_name": "order_number", "text": order_number})

        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": "es_PE"},
                "components": [{"type": "body", "parameters": parameters}]
            }
        }

        if status_id in {4, 6} and file:
            header_component = {
                "type": "header",
                "parameters": [
                    {
                        "type": "image",
                        "image": {
                            "link": f"{self.image_base_url}{file}"
                        }
                    }
                ]
            }
            payload["template"]["components"].insert(0, header_component)

        return self.post(payload)
    


    @handle_exceptions
    def confirm_flow_start(self, campaign, data):
        templates = {
            "shining_event": "mkt_shining_start"
        }
        
        parameters = [
            {"type": "text", "parameter_name": "name", "text": data.get("name")},
        ]

        payload = {
            "messaging_product": "whatsapp",
            "to": data.get("phone"),
            "type": "template",
            "template": {
                "name": templates.get(campaign),
                "language": {"code": "es_PE"},
                "components": [{"type": "body", "parameters": parameters}]
            }
        }
        return self.post(payload)
    

    @handle_exceptions
    def confirm_flow_yes(self, campaign, data):
        templates = {
            "shining_event": "mkt_shining_yes"
        }
        
        parameters = [
            {"type": "text", "parameter_name": "name", "text": data.get("name")},
        ]

        payload = {
            "messaging_product": "whatsapp",
            "to": data.get("phone"),
            "type": "template",
            "template": {
                "name": templates.get(campaign),
                "language": {"code": "es_PE"},
                "components": [{"type": "body", "parameters": parameters}]

            }
        }
        return self.post(payload)


    @handle_exceptions
    def confirm_flow_no(self, campaign, data):
        templates = {
            "shining_event": "mkt_shining_no"
        }

        parameters = [
            {"type": "text", "parameter_name": "name", "text": data.get("name")},
        ]
   
        payload = {
            "messaging_product": "whatsapp",
            "to": data.get("phone"),
            "type": "template",
            "template": {
                "name": templates.get(campaign),
                "language": {"code": "es_PE"},
                "components": [{"type": "body", "parameters": parameters}]
                
            }
        }
        return self.post(payload)


    @handle_exceptions
    def confirm_flow_reminder(self, phone):
        name ="Bambu Lab Fest"
        date ="Sábado 25 de octubre"
        schedule ="De 10:00 a.m. a 5:00 p.m."
        location ="Cámara de Comercio de Lima - Av. Giuseppe Garibaldi 396, Jesús María (Salón Carlos Ferreyros - Piso 7)"
        maps ="https://maps.app.goo.gl/sisjPduBcsqDRkji6"

        template_name = "confirm_flow_reminder"
        parameters = [
            {"type": "text", "parameter_name": "name", "text": name},
            {"type": "text", "parameter_name": "date", "text": date},
            {"type": "text", "parameter_name": "schedule", "text": schedule},
            {"type": "text", "parameter_name": "location", "text": location},
            {"type": "text", "parameter_name": "maps", "text": maps},
        ]

        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": "es_PE"},
                "components": [{"type": "body", "parameters": parameters}]
            }
        }
        return self.post(payload)
    

    @handle_exceptions
    def confirm_flow_reminder_2(self, phone):
        name ="Bambu Lab"
        name2 ="el evento de Krear 3D en la entrada"

        template_name = "confirm_flow_reminder_2"
        parameters = [
            {"type": "text", "parameter_name": "name", "text": name},
            {"type": "text", "parameter_name": "name2", "text": name2},
        ]

        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": "es_PE"},
                "components": [{"type": "body", "parameters": parameters}]
            }
        }
        return self.post(payload)
    

    @handle_exceptions
    def mkt_campaign(self, phone, template_name, header_image=None, parameters=None):
        components = []

        if header_image:
            components.append({
                "type": "header",
                "parameters": [{"type": "image", "image": {"link": header_image}}]
            })

        if parameters:
            components.append({"type": "body", "parameters": parameters})

        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": "es_PE"},
            }
        }
        if components:
            payload["template"]["components"] = components

        return self.post(payload)


    @handle_exceptions
    def send_odoo_invoice(self, client_phone, client_name, invoice_number, invoice_date, pdf_filename):
        payload = {
            "messaging_product": "whatsapp",
            # "to": "51946887982", # 996201441 "51946887982"
            "to": client_phone,
            "type": "template",
            "template": {
                "name": "odoo_invoice_prod",
                "language": {"code": "es_PE"},
                "components": [
                    {
                        "type": "header",
                        "parameters": [
                            {
                                "type": "document",
                                "document": {
                                    "link": f"{Odoo.PDF_URL}{pdf_filename}",
                                    "filename": pdf_filename
                                }
                            }
                        ],
                    },
                    {
                        "type": "body", 
                        "parameters": [
                            {
                                "type": "text",
                                "parameter_name": "name",
                                "text": client_name.title()
                            },
                            {
                                "type": "text",
                                "parameter_name": "number",
                                "text": invoice_number
                            },
                            {
                                "type": "text",
                                "parameter_name": "date",
                                "text": invoice_date
                            }
                        ]
                    }
                ]
            }
        }

        return self.post(payload)


    @handle_exceptions
    def refund_registered(self, phone, name, number, amount):
        parameters = [
            {"type": "text", "parameter_name": "name",   "text": name},
            {"type": "text", "parameter_name": "number", "text": number},
            {"type": "text", "parameter_name": "amount", "text": amount},
        ]
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "template",
            "template": {
                "name": "refunds_register",
                "language": {"code": "es_PE"},
                "components": [{"type": "body", "parameters": parameters}]
            }
        }
        return self.post(payload)


    @handle_exceptions
    def refund_approved_no_penalty(self, phone, name, number, amount):
        parameters = [
            {"type": "text", "parameter_name": "name",   "text": name},
            {"type": "text", "parameter_name": "number", "text": number},
            {"type": "text", "parameter_name": "amount", "text": amount},
        ]
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "template",
            "template": {
                "name": "refunds_no_penality",
                "language": {"code": "es_PE"},
                "components": [{"type": "body", "parameters": parameters}]
            }
        }
        return self.post(payload)


    @handle_exceptions
    def refund_approved_penalty(self, phone, name, number, amount, amount_final):
        parameters = [
            {"type": "text", "parameter_name": "name",         "text": name},
            {"type": "text", "parameter_name": "number",       "text": number},
            {"type": "text", "parameter_name": "amount",       "text": amount},
            {"type": "text", "parameter_name": "amount_final", "text": amount_final},
        ]
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "template",
            "template": {
                "name": "refunds_penality",
                "language": {"code": "es_PE"},
                "components": [{"type": "body", "parameters": parameters}]
            }
        }
        return self.post(payload)


    @handle_exceptions
    def refund_reverted(self, phone, name, number):
        parameters = [
            {"type": "text", "parameter_name": "name",   "text": name},
            {"type": "text", "parameter_name": "number", "text": number},
        ]
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "template",
            "template": {
                "name": "refunds_reverted",
                "language": {"code": "es_PE"},
                "components": [{"type": "body", "parameters": parameters}]
            }
        }
        return self.post(payload)


    @handle_exceptions
    def refund_executed(self, phone, name, number, amount, image_url=None):
        parameters = [
            {"type": "text", "parameter_name": "name",   "text": name},
            {"type": "text", "parameter_name": "number", "text": number},
            {"type": "text", "parameter_name": "amount", "text": amount},
        ]
        components = [{"type": "body", "parameters": parameters}]
        if image_url:
            components.insert(0, {
                "type": "header",
                "parameters": [{"type": "image", "image": {"link": f"{self.image_base_url}{image_url}"}}]
            })
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "template",
            "template": {
                "name": "refunds_executed",
                "language": {"code": "es_PE"},
                "components": components
            }
        }
        return self.post(payload)