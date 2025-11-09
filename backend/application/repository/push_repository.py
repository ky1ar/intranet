from application.handlers import handle_db_exceptions
from application.models import FireCloudTokens
from flask import g
from sqlalchemy import func


class PushRepository:
    @handle_db_exceptions
    def upsert_token(self, user_id, device_id, token):
        record = (
            g.db_session.query(FireCloudTokens)
            .filter(
                FireCloudTokens.user_id == user_id,
                FireCloudTokens.device_id == device_id,
            )
            .first()
        )

        if record:
            record.token = token
            record.updated_at = func.current_timestamp()
        else:
            record = FireCloudTokens(
                user_id=user_id,
                device_id=device_id,
                token=token,
            )
            g.db_session.add(record)

        g.db_session.commit()
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
