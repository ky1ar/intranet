import logging
from flask import g
from application.handlers import handle_db_exceptions
from application.utils import peru_time, normalize_phone
from application.db_models.prime_model import PrimeSubscription
from application.models import Clients

class PrimeRepository:
    
    @handle_db_exceptions
    def get_or_create_client(self, email, first_name=None, last_name=None, phone=None):
        """Busca al cliente por email. Si no existe, lo crea con datos básicos."""
        if not email:
            return None, 400
            
        client = (
            g.db_session.query(Clients)
            .filter(Clients.email == email)
            .first()
        )
        
        name = f"{first_name or ''} {last_name or ''}".strip() or email
        
        if not client:
            client = Clients(
                name=name,
                email=email,
                phone=normalize_phone(phone) if phone else None,
                document=""
            )
            g.db_session.add(client)
            g.db_session.flush()
            g.db_session.commit()
            
        return client, 200

    @handle_db_exceptions
    def get_subscription_by_culqi_id(self, culqi_id):
        sub = (
            g.db_session.query(PrimeSubscription)
            .filter(PrimeSubscription.culqi_subscription_id == culqi_id)
            .first()
        )
        return sub, 200

    @handle_db_exceptions
    def get_active_subscription_by_email(self, email):
        sub = (
            g.db_session.query(PrimeSubscription)
            .join(Clients)
            .filter(
                Clients.email == email,
                PrimeSubscription.status == 'active'
            )
            .first()
        )
        return sub, 200

    @handle_db_exceptions
    def create_subscription(self, client_id, culqi_id, plan_type):
        sub = PrimeSubscription(
            client_id=client_id,
            culqi_subscription_id=culqi_id,
            plan_type=plan_type,
            status="active",
            started_at=peru_time()
        )
        g.db_session.add(sub)
        g.db_session.commit()
        return sub, 200

    @handle_db_exceptions
    def update_subscription_status(self, culqi_id, new_status):
        sub = (
            g.db_session.query(PrimeSubscription)
            .filter(PrimeSubscription.culqi_subscription_id == culqi_id)
            .first()
        )
        if not sub:
            return "Suscripción no encontrada", 404
            
        sub.status = new_status
        g.db_session.commit()
        return sub, 200

    @handle_db_exceptions
    def get_all_subscriptions(self, status=None, plan_type=None):
        query = g.db_session.query(PrimeSubscription)
        
        if status:
            query = query.filter(PrimeSubscription.status == status)
        if plan_type:
            query = query.filter(PrimeSubscription.plan_type == plan_type)
            
        subs = query.order_by(PrimeSubscription.started_at.desc()).all()
        return subs, 200
