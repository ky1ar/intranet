from application.handlers import handle_db_exceptions
from application.models import FireCloudTokens
from flask import g
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError


class PushRepository:
    @handle_db_exceptions
    def upsert_token(self, user_id, device_id, token):
        session = g.db_session

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
            # Ya existe para ese user+device → solo actualizamos token (por si cambió)
            record.token = token
            record.updated_at = func.current_timestamp()
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
                existing_by_token.updated_at = func.current_timestamp()
            else:
                # 3) Token totalmente nuevo → insertar
                new_record = FireCloudTokens(
                    user_id=user_id,
                    device_id=device_id,
                    token=token,
                )
                session.add(new_record)

        try:
            session.commit()
        except IntegrityError:
            # Por si en una condición de carrera se metió otra fila igual
            session.rollback()

            # Intento final: actualizar por token
            existing_by_token = (
                session.query(FireCloudTokens)
                .filter(FireCloudTokens.token == token)
                .first()
            )
            if existing_by_token:
                existing_by_token.user_id = user_id
                existing_by_token.device_id = device_id
                existing_by_token.updated_at = func.current_timestamp()
                session.commit()
            else:
                # Si tampoco existe por token, re-lanzamos para que lo capture el decorador
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
