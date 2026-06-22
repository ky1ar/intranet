from datetime import datetime, timedelta, timezone
from application.handlers import handle_db_exceptions
from application.models import FireCloudTokens
from flask import g
from sqlalchemy.exc import IntegrityError


class PushRepository:
    def _now_peru(self):
        utc_now = datetime.now(timezone.utc)
        return utc_now - timedelta(hours=5)


    @handle_db_exceptions
    def get_tokens_by_users(self, user_ids):
        if not user_ids:
            return [], 200

        rows = (
            g.db_session.query(FireCloudTokens.token, FireCloudTokens.user_id)
            .filter(FireCloudTokens.user_id.in_(list(set(map(int, user_ids)))))
            .all()
        )
        return rows, 200

        
    @handle_db_exceptions
    def upsert_token(self, user_id, device_id, token, device_platform, user_agent):
        session = g.db_session
        now_peru = self._now_peru()

        # Normalizar por si vienen en None
        device_platform = device_platform or "unknown"
        user_agent = user_agent or ""

        # 1) Buscar por (user_id, device_id)
        record = (
            session.query(FireCloudTokens)
            .filter(
                FireCloudTokens.user_id == user_id,
                FireCloudTokens.device_id == device_id,
            )
            .first()
        )

        if record:
            # Ya existe para ese user+device → actualizar token + metadata
            record.token = token
            record.device_platform = device_platform
            record.user_agent = user_agent
            record.updated_at = now_peru
        else:
            # 2) No hay fila para ese user+device → ver si el token ya existe en otro lado
            existing_by_token = (
                session.query(FireCloudTokens)
                .filter(FireCloudTokens.token == token)
                .first()
            )

            if existing_by_token:
                # Reusar esa fila: reasignar user y device a este usuario/dispositivo
                existing_by_token.user_id = user_id
                existing_by_token.device_id = device_id
                existing_by_token.device_platform = device_platform
                existing_by_token.user_agent = user_agent
                existing_by_token.updated_at = now_peru
            else:
                # 3) Token totalmente nuevo → insertar
                new_record = FireCloudTokens(
                    user_id=user_id,
                    device_id=device_id,
                    token=token,
                    device_platform=device_platform,
                    user_agent=user_agent,
                    created_at=now_peru,
                    updated_at=now_peru,
                )
                session.add(new_record)

        try:
            session.commit()
        except IntegrityError:
            session.rollback()

            now_peru = self._now_peru()
            existing_by_token = (
                session.query(FireCloudTokens)
                .filter(FireCloudTokens.token == token)
                .first()
            )
            if existing_by_token:
                existing_by_token.user_id = user_id
                existing_by_token.device_id = device_id
                existing_by_token.device_platform = device_platform
                existing_by_token.user_agent = user_agent
                existing_by_token.updated_at = now_peru
                session.commit()
            else:
                raise

        return True, 200


    @handle_db_exceptions
    def delete_device(self, user_id, device_id):
        q = (
            g.db_session.query(FireCloudTokens)
            .filter(
                FireCloudTokens.user_id == user_id,
                FireCloudTokens.device_id == device_id,
            )
        )
        q.delete()
        g.db_session.commit()
        return True, 200


    @handle_db_exceptions
    def get_tokens_by_user(self, user_id):
        tokens = (
            g.db_session.query(FireCloudTokens)
            .filter(FireCloudTokens.user_id == user_id)
            .all()
        )
        return tokens or [], 200
