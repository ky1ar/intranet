import logging
from datetime import datetime
from flask import render_template
from flask_mail import Message
from application import mail, socketio
from application.handlers import handle_exceptions
from application.repository.prime_repository import PrimeRepository
from application.utils import format_datetime

# Diccionario que mapea los IDs de los planes de Culqi a 'lite' o 'full'
CULQI_PLAN_MAPPING = {
    "88ec7570-c8cb-46b7-9b45-d5178bd78458": "lite",
    "1672484e-ccee-4a28-b87e-4043c51caf0b": "full",
    "275a08d9-a846-451b-b485-449d9aa525fe": "lite", # Annual
    "79574840-afe9-45c1-a87d-f88a0af63360": "full", # Annual
}

class PrimeService:
    def __init__(self):
        self.repository = PrimeRepository()

    @handle_exceptions
    def process_webhook(self, event_type, data):
        """Procesa el webhook proveniente de Culqi (subscription.created, subscription.deleted)"""
        
        # Validar que sea un evento de suscripción
        if event_type not in ["subscription.created", "subscription.deleted"]:
            return "Evento ignorado", 200

        culqi_subscription_id = data.get("id")
        plan_id = data.get("plan_id")
        customer = data.get("customer", {})
        
        email = customer.get("email")
        metadata = customer.get("metadata", {})
        first_name = metadata.get("first_name") or customer.get("first_name")
        last_name = metadata.get("last_name") or customer.get("last_name")
        phone = customer.get("phone_number")
        
        if not email or not culqi_subscription_id:
            return "Faltan datos requeridos (email o subscription_id)", 400

        if event_type == "subscription.created":
            return self._handle_subscription_created(email, first_name, last_name, phone, culqi_subscription_id, plan_id)
        elif event_type == "subscription.deleted":
            return self._handle_subscription_deleted(culqi_subscription_id, email, first_name)
            
        return "OK", 200

    def _handle_subscription_created(self, email, first_name, last_name, phone, culqi_id, plan_id):
        # 1. Resolver el plan
        plan_type = CULQI_PLAN_MAPPING.get(plan_id)
        if not plan_type:
            logging.warning(f"Plan ID {plan_id} no está mapeado en K3D Prime.")
            # Default fallback si hay un plan no mapeado
            plan_type = "lite"

        # 2. Verificar si ya fue procesada (idempotencia)
        sub, sc = self.repository.get_subscription_by_culqi_id(culqi_id)
        if sc == 200 and sub:
            # Si ya existía y estaba cancelada, la reactivamos
            if sub.status != 'active':
                self.repository.update_subscription_status(culqi_id, 'active')
                socketio.emit("prime_update", {})
            return "Suscripción ya existía", 200

        # 3. Buscar o crear al cliente en nuestra base de datos general
        client, csc = self.repository.get_or_create_client(email, first_name, last_name, phone)
        if csc != 200:
            return "Error al buscar/crear cliente", 500
            
        # 4. Cancelar suscripciones antiguas activas de este mismo email
        # (Por si el usuario hace upgrade de Lite a Full)
        active_sub, asc = self.repository.get_active_subscription_by_email(email)
        if asc == 200 and active_sub and active_sub.culqi_subscription_id != culqi_id:
            self.repository.update_subscription_status(active_sub.culqi_subscription_id, "cancelled")

        # 5. Crear la nueva suscripción
        new_sub, sc = self.repository.create_subscription(client.id, culqi_id, plan_type)
        if sc != 200:
            return "Error al crear suscripción", 500

        # 6. Enviar correo de bienvenida
        self._send_welcome_email(email, first_name, plan_type)
        
        # 7. Notificar al frontend
        socketio.emit("prime_update", {})
        
        return "Suscripción procesada exitosamente", 200

    def _handle_subscription_deleted(self, culqi_id, email, first_name):
        sub, sc = self.repository.update_subscription_status(culqi_id, "cancelled")
        if sc == 200:
            self._send_cancellation_email(email, first_name)
            socketio.emit("prime_update", {})
        return "Suscripción cancelada", 200

    @handle_exceptions
    def get_all_subscriptions(self, status=None, plan_type=None):
        subs, sc = self.repository.get_all_subscriptions(status, plan_type)
        if sc != 200:
            return subs, sc
            
        return [{
            "id": s.id,
            "client_name": s.client.name if s.client else 'Sin Nombre',
            "email": s.client.email if s.client else 'Sin Email',
            "phone": s.client.phone if s.client else None,
            "culqi_subscription_id": s.culqi_subscription_id,
            "plan_type": s.plan_type,
            "status": s.status,
            "started_at": format_datetime(s.started_at)
        } for s in subs], 200

    @handle_exceptions
    def verify_prime_status(self, email):
        """Usado por WooCommerce vía API para saber si aplicar descuentos"""
        sub, sc = self.repository.get_active_subscription_by_email(email)
        if sc != 200 or not sub:
            return {"is_prime": False}, 200
            
        return {
            "is_prime": True,
            "plan_type": sub.plan_type,
            "started_at": sub.started_at.isoformat() if sub.started_at else None
        }, 200

    def _send_welcome_email(self, email, name, plan_type):
        try:
            html_content = render_template(
                "prime_welcome.html",
                client_name=name or "Comunidad K3D",
                plan_type=plan_type.upper(),
                current_year=datetime.now().year
            )
            msg = Message(
                subject=f"¡Bienvenido a K3D Prime {plan_type.capitalize()}!",
                sender=("Krear 3D", "web@tiendakrear3d.com"),
                recipients=[email],
                html=html_content
            )
            mail.send(msg)
        except Exception as e:
            logging.exception("Error enviando correo de bienvenida Prime a %s", email)

    def _send_cancellation_email(self, email, name):
        try:
            html_content = render_template(
                "prime_cancelled.html",
                client_name=name or "Comunidad K3D",
                current_year=datetime.now().year
            )
            msg = Message(
                subject="Tu suscripción a K3D Prime ha sido cancelada",
                sender=("Krear 3D", "web@tiendakrear3d.com"),
                recipients=[email],
                html=html_content
            )
            mail.send(msg)
        except Exception as e:
            logging.exception("Error enviando correo de cancelación Prime a %s", email)
