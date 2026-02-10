import logging
from application.handlers import handle_db_exceptions
from application.db_models.complaint_model import ComplaintStatus, ComplaintConsumption, ComplaintRequest, ComplaintRequestStatus, ComplaintType, ComplaintAttachment, ComplaintChats, ComplaintCategory
from application.utils import peru_time
from flask import g
from flask_jwt_extended import get_jwt_identity


class ComplaintRepository:
    @handle_db_exceptions
    def new_complaint(self, data):
        new_complaint = ComplaintRequest(
            client_id=data.get("client_id"),
            is_minor=data.get("is_minor"),
            order_number=data.get("order_number"),
            complaint_consumption_id=data.get("consumption_id"),
            amount=data.get("amount"),
            purchase_date=data.get("purchase_date"),
            consumption_description=data.get("description"),
            complaint_type_id=data.get("type_id"),
            detail=data.get("detail"),
            customer_request=data.get("request"),
            declaration_accepted=1,
            status_id=1,
            created_at=peru_time(),
        )

        g.db_session.add(new_complaint)
        g.db_session.flush()
        complaint_id = new_complaint.id
        g.db_session.commit()
        return complaint_id, 200
    

    @handle_db_exceptions
    def get_statuses(self):
        status = g.db_session.query(ComplaintStatus).order_by(ComplaintStatus.id.asc()).all()
        if not status:
            return [], 200

        return status, 200


    @handle_db_exceptions
    def get_complaints(self, user_id=None):
        query = g.db_session.query(ComplaintRequest).filter(ComplaintRequest.status_id != 9)

        if user_id:
            pass
            # query = query.filter(ComplaintRequest.user_id == user_id)

        complaints = query.all()

        if not complaints:
            return [], 200

        return complaints, 200
    

    @handle_db_exceptions
    def get_complaint_status(self, complaint_id, status_id):
        complaint = (
            g.db_session.query(ComplaintRequestStatus)
            .filter(ComplaintRequestStatus.complaint_id == complaint_id, ComplaintRequestStatus.status_id == status_id)
            .first()
        )
        if not complaint:
            return 'Reclamo no localizado', 404

        return complaint, 200
    

    @handle_db_exceptions
    def get_complaint(self, complaint_id):
        complaint = (
            g.db_session.query(ComplaintRequest)
            .filter(ComplaintRequest.id == complaint_id)
            .first()
        )
        if not complaint:
            return 'No localizado', 404

        return complaint, 200


    @handle_db_exceptions
    def get_complaint_history(self, complaint_id):
        history = (
            g.db_session.query(ComplaintRequestStatus)
            .filter(ComplaintRequestStatus.complaint_id == complaint_id)
            .all()
        )
        if not history:
            return [], 200

        return history, 200
    

    @handle_db_exceptions
    def move_status(self, complaint, current_status_id, data):
        if current_status_id == 2:
            complaint.owner_id = data.get("owner_id")
            complaint.seller_id = data.get("seller_id")
            complaint.category_id = data.get("category_id")

        complaint.status_id = current_status_id + 1
        resolved = data.get("resolved")
        if resolved:
            complaint.resolved = resolved

        g.db_session.add(complaint)
        g.db_session.commit()
        return True, 200
    

    @handle_db_exceptions
    def new_history(self, complaint_id, user_id, current_status_id, notes):
        new_order_status = ComplaintRequestStatus(
            complaint_id=complaint_id,
            status_id=current_status_id + 1,
            user_id=user_id,
            notes=notes,
            created_at=peru_time(),
        )
        g.db_session.add(new_order_status)
        g.db_session.commit()
        return True, 200
    

    @handle_db_exceptions
    def complaint_exists(self, complaint_id: int):
        exists = (
            g.db_session.query(ComplaintRequest.id)
            .filter(ComplaintRequest.id == complaint_id)
            .first()
        )
        return bool(exists), 200


    @handle_db_exceptions
    def add_attachment(self, complaint_id, user_id, original_name, stored_name, mime_type, size_bytes):
        row = ComplaintAttachment(
            complaint_id=complaint_id,
            uploaded_by=user_id,
            original_name=original_name,
            stored_name=stored_name,
            mime_type=mime_type,
            size_bytes=size_bytes,
            created_at=peru_time(),
        )
        g.db_session.add(row)
        g.db_session.commit()
        return row.id, 200


    @handle_db_exceptions
    def get_attachments(self, complaint_id):
        rows = (
            g.db_session.query(ComplaintAttachment)
            .filter(ComplaintAttachment.complaint_id == complaint_id)
            .order_by(ComplaintAttachment.id.desc())
            .all()
        )
        return rows or [], 200


    @handle_db_exceptions
    def get_attachment_by_id(self, attachment_id):
        row = (
            g.db_session.query(ComplaintAttachment)
            .filter(ComplaintAttachment.id == attachment_id)
            .first()
        )
        if not row:
            return "Not found", 404
        return row, 200
    

    @handle_db_exceptions
    def get_options_type(self):
        types = (
            g.db_session.query(ComplaintType)
            .order_by(ComplaintType.id)
            .all()
        )
        
        if not types:
            return [], 400
        return types, 200


    @handle_db_exceptions
    def get_options_consumption(self):
        consumptions = (
            g.db_session.query(ComplaintConsumption)
            .order_by(ComplaintConsumption.id)
            .all()
        )
        
        if not consumptions:
            return [], 400
        return consumptions, 200


    @handle_db_exceptions
    def get_options_categories(self):
        categories = (
            g.db_session.query(ComplaintCategory)
            .order_by(ComplaintCategory.id)
            .all()
        )
        
        if not categories:
            return [], 400
        return categories, 200


    @handle_db_exceptions
    def add_chat(self, complaint_id, user_id, comment):
        chat = ComplaintChats(
            complaint_id=complaint_id,
            commenter_id=user_id,
            comment=comment,
            created_at=peru_time(),
        )
        g.db_session.add(chat)
        g.db_session.commit()
        g.db_session.refresh(chat)
        return chat, 200


    @handle_db_exceptions
    def get_chat_participants(self, complaint_id, exclude_user_id = None, include_owners = True):
        q = (g.db_session.query(ComplaintChats.commenter_id).filter(ComplaintChats.complaint_id == complaint_id))

        if exclude_user_id is not None:
            q = q.filter(ComplaintChats.commenter_id != exclude_user_id)

        user_ids = [row[0] for row in q.distinct().all()]

        if include_owners:
            owner_id = (
                g.db_session.query(ComplaintRequest.owner_id)
                .filter(ComplaintRequest.id == complaint_id)
                .scalar()
            )
            if owner_id and owner_id != exclude_user_id and owner_id not in user_ids:
                user_ids.append(owner_id)

            seller_id = (
                g.db_session.query(ComplaintRequest.seller_id)
                .filter(ComplaintRequest.id == complaint_id)
                .scalar()
            )
            if seller_id and seller_id != exclude_user_id and seller_id not in user_ids:
                user_ids.append(seller_id)

        return user_ids, 200