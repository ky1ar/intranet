import requests, logging, json
from firebase_admin import messaging
from application.repository.push_repository import PushRepository
from application.handlers import handle_exceptions


class PushSender:
    def __init__(self):
        self.push_repository = PushRepository()


    @handle_exceptions
    def send_to_user(self, user_id, title, body, data=None):
        tokens, tc = self.push_repository.get_tokens_by_user(user_id)
        if tc != 200 or not tokens:
            logging.info(f"[FCM] Usuario {user_id} sin tokens; status={tc}")
            return {
                "success": False,
                "message": "Sin tokens"
            }, 200

        registration_tokens = [t.token for t in tokens]

        raw_data = data or {}
        safe_data = {}
        for k, v in raw_data.items():
            if v is None:
                continue
            if isinstance(v, (dict, list)):
                safe_data[str(k)] = json.dumps(v, ensure_ascii=False)
            else:
                safe_data[str(k)] = str(v)

        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=safe_data,
            tokens=registration_tokens,
        )

        try:
            response = messaging.send_each_for_multicast(message)

            logging.info(
                f"[FCM] Enviadas {response.success_count} ok, "
                f"{response.failure_count} con error para user_id={user_id}"
            )

            return {
                "success": True,
                "message": "Notificación enviada",
                "sent": response.success_count,
                "failed": response.failure_count,
            }, 200

        except Exception as e:
            logging.exception(f"[FCM] Error al enviar notificación a user_id={user_id}: {e}")
            return {"success": False, "message": "Error al enviar notificación"}, 500


    @handle_exceptions
    def send_to_users(self, user_ids, title, body, data=None):
        if not user_ids:
            return {
                "success": False,
                "message": "Lista de usuarios vacía"
            }, 400

        raw_data = data or {}
        safe_data = {}
        for k, v in raw_data.items():
            if v is None:
                continue
            if isinstance(v, (dict, list)):
                safe_data[str(k)] = json.dumps(v, ensure_ascii=False)
            else:
                safe_data[str(k)] = str(v)

        total_sent = 0
        total_failed = 0
        users_without_tokens = []

        for user_id in user_ids:
            tokens, tc = self.push_repository.get_tokens_by_user(user_id)

            if tc != 200 or not tokens:
                users_without_tokens.append(user_id)
                continue

            registration_tokens = [t.token for t in tokens]

            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=safe_data,
                tokens=registration_tokens,
            )

            try:
                response = messaging.send_each_for_multicast(message)

                total_sent += response.success_count
                total_failed += response.failure_count

                logging.info(
                    f"[FCM] user_id={user_id} → "
                    f"{response.success_count} ok, "
                    f"{response.failure_count} error"
                )

            except Exception as e:
                logging.exception(
                    f"[FCM] Error enviando a user_id={user_id}: {e}"
                )
                total_failed += len(registration_tokens)

        return {
            "success": True,
            "message": "Notificaciones procesadas",
            "sent": total_sent,
            "failed": total_failed,
            "users_without_tokens": users_without_tokens,
        }, 200