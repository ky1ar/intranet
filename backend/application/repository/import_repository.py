import logging
from application.utils import peru_time
from application.handlers import handle_db_exceptions
from application.db_models.import_model import (
    ImportShipment, ImportBusiness, ImportIncoterm, ImportPort, ImportProvider,
    ImportStatus, ImportStatusHistory, ImportType, ImportAttachment, ImportChats,
    ImportShipmentLine
)
from flask import g
from sqlalchemy import or_


class ImportRepository:
    @handle_db_exceptions
    def get_statuses(self):
        status = g.db_session.query(ImportStatus).order_by(ImportStatus.id.asc()).all()
        if not status:
            return [], 200

        return status, 200


    @handle_db_exceptions
    def get_imports(self):
        imports = (
            g.db_session.query(ImportShipment)
            .filter(ImportShipment.status_id != 1)
            .filter(ImportShipment.status_id != 14)
            .all()
        )
        return imports or [], 200


    @handle_db_exceptions
    def search_imports(self, term, limit=20):
        like = f"%{term}%"
        rows = (
            g.db_session.query(ImportShipment)
            .outerjoin(ImportShipmentLine, ImportShipmentLine.import_shipment_id == ImportShipment.id)
            .outerjoin(ImportProvider, ImportShipmentLine.provider_id == ImportProvider.id)
            .filter(ImportShipment.status_id != 1)
            .filter(or_(
                ImportProvider.name.ilike(like),
                ImportShipment.local_agent_name.ilike(like),
                ImportShipment.origin_agent_name.ilike(like),
            ))
            .order_by(ImportShipment.id.desc())
            .distinct()
            .limit(limit)
            .all()
        )
        return rows or [], 200


    @handle_db_exceptions
    def get_imports_paginated(self, page=1, per_page=12):
        q = (
            g.db_session.query(ImportShipment)
            .filter(ImportShipment.status_id != 1)
        )
        total = q.count()
        items = (
            q.order_by(ImportShipment.id.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return {
            "list": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,
        }, 200
    

    @handle_db_exceptions
    def get_status_history(self, import_shipment_id, status_id):
        history = (
            g.db_session.query(ImportStatusHistory)
            .filter(ImportStatusHistory.import_shipment_id == import_shipment_id, ImportStatusHistory.status_id == status_id)
            .first()
        )
        if not history:
            return 'Reclamo no localizado', 404

        return history, 200
    

    @handle_db_exceptions
    def get_options_type(self):
        types = (
            g.db_session.query(ImportType)
            .order_by(ImportType.id)
            .all()
        )
        
        if not types:
            return [], 400
        return types, 200


    @handle_db_exceptions
    def get_options_provider(self):
        providers = (
            g.db_session.query(ImportProvider)
            .order_by(ImportProvider.name)
            .all()
        )
        
        if not providers:
            return [], 400
        return providers, 200


    @handle_db_exceptions
    def update_draft_agents(self, import_shipment, local_agent, origin_agent):
        import_shipment.local_agent_name = local_agent
        import_shipment.origin_agent_name = origin_agent
        g.db_session.add(import_shipment)
        g.db_session.commit()
        return True, 200

    
    @handle_db_exceptions
    def delete_import_draft(self, import_shipment_id):
        # eliminar hijos primero (por si no hay cascade en DB)
        g.db_session.query(ImportChats).filter(
            ImportChats.import_shipment_id == import_shipment_id
        ).delete(synchronize_session=False)

        g.db_session.query(ImportAttachment).filter(
            ImportAttachment.import_shipment_id == import_shipment_id
        ).delete(synchronize_session=False)

        g.db_session.query(ImportStatusHistory).filter(
            ImportStatusHistory.import_shipment_id == import_shipment_id
        ).delete(synchronize_session=False)

        g.db_session.query(ImportShipmentLine).filter(
            ImportShipmentLine.import_shipment_id == import_shipment_id
        ).delete(synchronize_session=False)

        g.db_session.query(ImportShipment).filter(
            ImportShipment.id == import_shipment_id
        ).delete(synchronize_session=False)

        g.db_session.commit()
        return True, 200


    @handle_db_exceptions
    def get_options_business(self):
        items = (
            g.db_session.query(ImportBusiness)
            .order_by(ImportBusiness.id)
            .all()
        )
        
        if not items:
            return [], 400
        return items, 200


    @handle_db_exceptions
    def get_options_incoterm(self):
        incoterms = (
            g.db_session.query(ImportIncoterm)
            .order_by(ImportIncoterm.id)
            .all()
        )
        
        if not incoterms:
            return [], 400
        return incoterms, 200


    @handle_db_exceptions
    def get_options_port(self):
        ports = (
            g.db_session.query(ImportPort)
            .order_by(ImportPort.id)
            .all()
        )
        
        if not ports:
            return [], 400
        return ports, 200


    @handle_db_exceptions
    def get_provider(self, provider_id):
        provider = (
            g.db_session.query(ImportProvider)
            .filter(
                ImportProvider.id == provider_id
            )
            .first()
        )
        if not provider:
            return "Proveedor no encontrado", 404

        return provider, 200


    @handle_db_exceptions
    def new_import(self, data):
        lines = data.get("lines") or []
        if not isinstance(lines, list) or not lines:
            return "Debe enviar al menos una línea", 400

        new_import = ImportShipment(
            business_id=int(data.get("business_id")),
            type_id=int(data.get("type_id")),
            port_id=data.get("port_id"),
            custom_port_name=data.get("custom_port_name"),
            status_id=1,
            fcl=int(data.get("fcl") or 0),
            local_agent_name=(data.get("local_agent") or "").strip(),
            origin_agent_name=(data.get("origin_agent") or "").strip(),
            reference=data.get("reference"),
        )

        g.db_session.add(new_import)
        g.db_session.flush()

        for idx, line in enumerate(lines, start=1):
            row = ImportShipmentLine(
                import_shipment_id=new_import.id,
                provider_id=int(line.get("provider_id")),
                incoterm_id=line.get("incoterm_id"),
                custom_incoterm_name=line.get("custom_incoterm_name"),
                advance_payment_percent=line.get("advance_payment_percent"),
                balance_days=line.get("balance_days"),
                position=idx,
                po_number=line.get("po_number"),
            )
            g.db_session.add(row)

        g.db_session.commit()
        return new_import.id, 200


    @handle_db_exceptions
    def new_history(self, import_id, user_id, current_status_id, notes=None, down=False):
        new_order_status = ImportStatusHistory(
            import_shipment_id=import_id,
            status_id=current_status_id + (-1 if down else 1),
            user_id=user_id,
            notes=notes,
            created_at=peru_time(),
        )
        g.db_session.add(new_order_status)
        g.db_session.commit()
        return True, 200
    

    @handle_db_exceptions
    def get_by_status(self, status_id):
        imports = (
            g.db_session.query(ImportShipment)
            .filter(ImportShipment.status_id == status_id)
            .all()
        )
        return imports or [], 200


    @handle_db_exceptions
    def get_import(self, import_id):
        import_shipment = (
            g.db_session.query(ImportShipment)
            .filter(ImportShipment.id == import_id)
            .first()
        )
        if not import_shipment:
            return 'No localizado', 404

        return import_shipment, 200


    @handle_db_exceptions
    def get_import_history(self, import_id, status_id):
        history = (
            g.db_session.query(ImportStatusHistory)
            .filter(ImportStatusHistory.import_shipment_id == import_id, ImportStatusHistory.status_id == status_id)
            .first()
        )
        if not history:
            return 'Estado no localizado, verifique los datos', 400

        return history, 200

        
    @handle_db_exceptions
    def move_status(self, import_shipment, current_status_id, data, down=False):
        if not down:
            if current_status_id == 2:
                import_shipment.booking_date = data.get("booking_date")

            if current_status_id == 5:
                import_shipment.etd_date = data.get("etd_date")
                import_shipment.eta_date = data.get("eta_date")
                import_shipment.qty = data.get("qty")
                import_shipment.pallets = data.get("pallets")
                import_shipment.weight = data.get("weight")
                import_shipment.volume = data.get("volume")
                import_shipment.tracking_link = data.get("tracking_link")

            if current_status_id == 7:
                import_shipment.deadline_date = data.get("deadline_date")

            if current_status_id == 8:
                import_shipment.tax_amount = data.get("tax_amount")
                import_shipment.tax_currency = data.get("tax_currency") or "PEN"
                import_shipment.perception_amount = data.get("perception_amount")
                import_shipment.perception_currency = data.get("perception_currency") or "PEN"
                import_shipment.dua_number = (data.get("dua_number") or "").strip() or None

            if current_status_id == 9:
                import_shipment.pay_date = data.get("pay_date")
                import_shipment.traffic_light = data.get("traffic_light")

            if current_status_id == 12:
                import_shipment.delivery_date = data.get("delivery_date")
                import_shipment.delivery_time = data.get("delivery_time")
                import_shipment.delivery_name = data.get("delivery_name")
                import_shipment.delivery_phone = data.get("delivery_phone")
                import_shipment.delivery_code = data.get("delivery_code")

        import_shipment.status_id = current_status_id + (-1 if down else 1)

        g.db_session.add(import_shipment)
        g.db_session.commit()
        return True, 200
    

    @handle_db_exceptions
    def get_attachments(self, import_id, target):
        rows = (
            g.db_session.query(ImportAttachment)
            .filter(ImportAttachment.import_shipment_id == import_id)
            .filter(ImportAttachment.target == target)
            .order_by(ImportAttachment.id.desc())
            .all()
        )
        return rows or [], 200


    @handle_db_exceptions
    def get_attachments_by_import(self, import_id):
        rows = (
            g.db_session.query(ImportAttachment)
            .filter(ImportAttachment.import_shipment_id == import_id)
            .order_by(ImportAttachment.id.desc())
            .all()
        )
        return rows or [], 200


    @handle_db_exceptions
    def get_attachment_by_id(self, attachment_id):
        row = (
            g.db_session.query(ImportAttachment)
            .filter(ImportAttachment.id == attachment_id)
            .first()
        )
        if not row:
            return "Not found", 404
        return row, 200


    @handle_db_exceptions
    def add_chat(self, import_id, user_id, comment):
        chat = ImportChats(
            import_shipment_id=import_id,
            commenter_id=user_id,
            comment=comment,
            created_at=peru_time(),
        )
        g.db_session.add(chat)
        g.db_session.commit()
        g.db_session.refresh(chat)
        return chat, 200
    

    @handle_db_exceptions
    def get_chat_participants(self, import_id, exclude_user_id = None):
        q = (g.db_session.query(ImportChats.commenter_id).filter(ImportChats.import_shipment_id == import_id))

        if exclude_user_id is not None:
            q = q.filter(ImportChats.commenter_id != exclude_user_id)

        user_ids = [row[0] for row in q.distinct().all()]
        return user_ids, 200


    @handle_db_exceptions
    def add_attachment(self, import_id, user_id, target, original_name, stored_name, mime_type, size_bytes):
        row = ImportAttachment(
            import_shipment_id=import_id,
            target=target,
            user_id=user_id,
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
    def update_basic(self, import_shipment, data):
        import_shipment.port_id = data.get("port_id")
        import_shipment.business_id = data.get("business_id")
        import_shipment.type_id = data.get("type_id")
        import_shipment.fcl = int(data.get("fcl") or 0)
        import_shipment.custom_port_name = data.get("custom_port_name")
        import_shipment.local_agent_name = data.get("local_agent_name")
        import_shipment.origin_agent_name = data.get("origin_agent_name")
        import_shipment.reference = data.get("reference")

        g.db_session.add(import_shipment)

        g.db_session.query(ImportShipmentLine).filter(
            ImportShipmentLine.import_shipment_id == import_shipment.id
        ).delete(synchronize_session=False)

        for row in data.get("lines", []):
            g.db_session.add(
                ImportShipmentLine(
                    import_shipment_id=import_shipment.id,
                    provider_id=row.get("provider_id"),
                    incoterm_id=row.get("incoterm_id"),
                    custom_incoterm_name=row.get("custom_incoterm_name"),
                    advance_payment_percent=row.get("advance_payment_percent"),
                    balance_days=row.get("balance_days"),
                    position=row.get("position"),
                    po_number=row.get("po_number"),
                )
            )

        g.db_session.commit()
        return True, 200


    @handle_db_exceptions
    def update_eta(self, import_shipment_id, new_eta_date):
        shipment = (
            g.db_session.query(ImportShipment)
            .filter(ImportShipment.id == import_shipment_id)
            .first()
        )
        if not shipment:
            return "No localizado", 404
        shipment.eta_date = new_eta_date
        g.db_session.add(shipment)
        g.db_session.commit()
        return True, 200


    @handle_db_exceptions
    def set_status(self, import_shipment, status_id):
        import_shipment.status_id = status_id
        g.db_session.add(import_shipment)
        g.db_session.commit()
        return True, 200

    @handle_db_exceptions
    def new_history_exact(self, import_id, user_id, status_id, notes=None):
        row = ImportStatusHistory(
            import_shipment_id=import_id,
            status_id=status_id,
            user_id=user_id,
            notes=notes,
            created_at=peru_time(),
        )
        g.db_session.add(row)
        g.db_session.commit()
        return True, 200