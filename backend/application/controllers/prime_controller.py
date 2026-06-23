import json
import logging
from flask import request
from application.services.prime_service import PrimeService

prime_service = PrimeService()

class PrimeController:
    
    def webhook(self):
        """Endpoint que recibe notificaciones desde Culqi"""
        try:
            data = request.json
            if not data:
                return {"message": "Invalid JSON"}, 400
                
            event_type = data.get("type")
            event_data = data.get("data", {})
            
            result, sc = prime_service.process_webhook(event_type, event_data)
            return {"message": result}, sc
            
        except Exception as e:
            logging.exception("Error procesando webhook de Culqi Prime")
            return {"message": "Internal Server Error"}, 500

    def get_all(self):
        """Devuelve la lista de suscripciones Prime para la vista de Intranet"""
        status = request.args.get("status")
        plan_type = request.args.get("plan_type")
        
        subs, sc = prime_service.get_all_subscriptions(status, plan_type)
        if sc != 200:
            return {"message": subs}, sc
            
        return {"data": subs}, 200

    def verify(self):
        """Endpoint consumido por WooCommerce para verificar si un email es Prime"""
        email = request.args.get("email")
        if not email:
            return {"message": "El parámetro email es requerido"}, 400
            
        result, sc = prime_service.verify_prime_status(email)
        return result, sc
