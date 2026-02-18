import logging
from application.handlers import handle_db_exceptions
from application.db_models.import_model import ImportShipment, ImportBusiness, ImportIncoterm, ImportPort, ImportProvider, ImportStatus, ImportStatusHistory, ImportType, ImportAttachment
from application.utils import peru_time
from flask import g


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
        if not imports:
            return [], 200

        return imports, 200
    

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
            .order_by(ImportProvider.id)
            .all()
        )
        
        if not providers:
            return [], 400
        return providers, 200


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
        new_import = ImportShipment(
            provider_id = int(data.get("provider_id")),
            business_id = int(data.get("business_id")),
            type_id = int(data.get("type_id")),
            incoterm_id = int(data.get("incoterm_id")),
            port_id = int(data.get("port_id")),
            status_id = 1,
            local_agent_name = data.get("local_agent"),
            origin_agent_name = data.get("origin_agent"),
        )

        g.db_session.add(new_import)
        g.db_session.flush()
        import_id = new_import.id
        g.db_session.commit()
        return import_id, 200


    @handle_db_exceptions
    def new_history(self, import_id, user_id, current_status_id, notes):
        new_order_status = ImportStatusHistory(
            import_shipment_id=import_id,
            status_id=current_status_id + 1,
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
            # .filter(ShippingOrders.is_deleted.is_(False))
            .all()
        )

        if not imports:
            return 'No se encontraron ordenes de pedido para este estado', 404
        
        return imports, 200


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
    def move_status(self, import_shipment, current_status_id, data):
        if current_status_id == 2:
            import_shipment.booking_date = data.get("booking_date")

        if current_status_id == 5:
            import_shipment.etd_date = data.get("etd_date")
            import_shipment.eta_date = data.get("eta_date")
            import_shipment.qty = data.get("qty")
            import_shipment.pallets = data.get("pallets")
            import_shipment.weight = data.get("weight")
            import_shipment.volume = data.get("volume")

        if current_status_id == 7:
            import_shipment.deadline_date = data.get("deadline_date")

        if current_status_id == 9:
            import_shipment.pay_date = data.get("pay_date")
            import_shipment.traffic_light = data.get("traffic_light")

        if current_status_id == 12:
            import_shipment.delivery_date = data.get("delivery_date")
            import_shipment.delivery_time = data.get("delivery_time")
            import_shipment.delivery_name = data.get("delivery_name")
            import_shipment.delivery_phone = data.get("delivery_phone")
            import_shipment.delivery_code = data.get("delivery_code")

        import_shipment.status_id = current_status_id + 1

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