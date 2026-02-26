import logging, os, uuid
from datetime import date
from werkzeug.utils import secure_filename
from flask import request, send_file, render_template
from flask_jwt_extended import get_jwt_identity
from application.handlers import handle_exceptions
from application.utils import format_time, calculate_passed_days, format_date, size, file_extension, allowed_extension, upload_path, format_name, format_datetime
from application.repository.import_repository import ImportRepository
from application.repository.user_repository import UserRepository
from application.repository.client_repository import ClientRepository
from application.services.push_service import PushSender
from application import socketio
from config import Paths


try:
    from docx import Document
except Exception:
    Document = None

try:
    import openpyxl
except Exception:
    openpyxl = None



class ImportService:
    def __init__(self):
        self.import_repository = ImportRepository()
        self.client_repository = ClientRepository()
        self.user_repository = UserRepository()
        self.push_service = PushSender()
        self.worker_lvl = 2
        self.leader_lvl = 3
        self.admin_lvl = 4
        self.fabrix_id = 21
        self.admin_dep = 1


    @handle_exceptions
    def status(self):
        status, sc = self.import_repository.get_statuses()
        if sc != 200:
            return status, sc
        
        status_list = [
            {
                "id": option.id,
                "name": option.name,
                "image": option.image,

            } for option in status
        ]
        return status_list, 200
    
    
    @handle_exceptions
    def get_by_status(self, status_id):
        imports, isc = self.import_repository.get_by_status(status_id)
        if isc != 200:
            return imports, isc
        
        result = []
        for item in imports:
            order_data = {
                "id": item.id,
                "provider_name": item.provider.name,
                "business_name": item.business.name,
                "status_id": item.status_id,
                "type_id": item.type_id,
            }

            result.append(order_data)
        return result, 200


    def _serialize_attachment(self, r):
        return {
            "id": r.id,
            "target": r.target,
            "original_name": r.original_name,
            "mime_type": r.mime_type,
            "size_bytes": r.size_bytes,
            "size_h": size(r.size_bytes),
            "created_at": str(r.created_at),
            "ext": file_extension(r.original_name),

            "inline_url": f"/imports/attachment/{r.id}?disposition=inline",
            "download_url": f"/imports/attachment/{r.id}?disposition=attachment",
            "preview_url": f"/imports/attachment/{r.id}/preview",
        }

    @handle_exceptions
    def dashboard(self):
        user_id = int(get_jwt_identity())
        user, uc = self.user_repository.get_user_by_id(user_id)
        if uc != 200:
            return user, uc

        imports, cc = self.import_repository.get_imports() 
        if cc != 200:
            return imports, cc

        statuses, sc = self.import_repository.get_statuses() 
        if sc != 200:
            return statuses, sc
        
        result = []
        for status in statuses:
            if status.id == 1 or status.id == 14:
                continue

            import_status = [import_row for import_row in imports if import_row.status_id == status.id]
            
            imports_list = []
            for item in import_status:
                passed_days = 0
                updated_today = False

                first_status, _ = self.import_repository.get_status_history(item.id, 1) 
                if first_status:
                    passed_days = calculate_passed_days(first_status.created_at)

                current_status, _ = self.import_repository.get_status_history(item.id, status.id) 
                if current_status and current_status.created_at.date() == date.today():
                    updated_today = True

                imports_data = {
                    "id": item.id,
                    "provider_name": item.provider.name,
                    "business_name": item.business.name,
                    "type_id": item.type_id,
                    "type_letter": "SP",
                    "updated_today": updated_today,
                    "passed_days": passed_days,
                    "status_id": status.id,
                    "traffic_light": item.traffic_light,
                }
                    
                imports_list.append(imports_data)
            
            imports_list.sort(key=lambda x: x["passed_days"], reverse=True)

            result.append({
                "status_id": status.id,
                "status_name": status.name,
                "imports": imports_list
            })
        return result, 200
    

    @handle_exceptions
    def options_provider(self):
        providers, cc = self.import_repository.get_options_provider() 
        if cc != 200:
            return providers, cc
        
        result = []
        for provider in providers:
            result.append({
                "id": provider.id,
                "name": provider.name
            })
        return result, 200


    @handle_exceptions
    def options_type(self):
        types, tc = self.import_repository.get_options_type() 
        if tc != 200:
            return types, tc
        
        result = []
        for item in types:
            result.append({
                "id": item.id,
                "name": item.name
            })
        return result, 200


    @handle_exceptions
    def options_business(self):
        business, cc = self.import_repository.get_options_business() 
        if cc != 200:
            return business, cc
        
        result = []
        for item in business:
            result.append({
                "id": item.id,
                "name": item.name
            })
        return result, 200
    

    @handle_exceptions
    def options_incoterm(self):
        incoterms, cc = self.import_repository.get_options_incoterm() 
        if cc != 200:
            return incoterms, cc
        
        result = []
        for incoterm in incoterms:
            result.append({
                "id": incoterm.id,
                "code": incoterm.code
            })
        return result, 200


    @handle_exceptions
    def options_port(self):
        ports, cc = self.import_repository.get_options_port() 
        if cc != 200:
            return ports, cc
        
        result = []
        for port in ports:
            result.append({
                "id": port.id,
                "name": port.name.title()
            })
        return result, 200
    

    @handle_exceptions
    def get_provider(self, provider_id):
        provider, pc = self.import_repository.get_provider(provider_id)
        if pc != 200:
            return provider, pc

        response = {
            "id": provider.id,
            "name": provider.name,
            "contact": provider.contact,
            "letter": provider.name[0].title(),
            "email": provider.email,
            "phone": provider.phone,
            "telephone": provider.telephone,
        }
        return response, 200
    

    @handle_exceptions
    def view(self, import_id):
        import_shipment, isc = self.import_repository.get_import(import_id) 
        if isc != 200:
            return import_shipment, isc

        register_days = 0
        import_history, ihc = self.import_repository.get_import_history(import_id, 2) 
        if ihc == 200:
            register_days = calculate_passed_days(import_history.created_at)

        order_data = {
            "id": import_shipment.id,
            "passed_days": f"{register_days}  día{'' if register_days == 1 else 's'}",
            "provider": {
                "name": import_shipment.provider.name,
                "contact": import_shipment.provider.contact,
                "email": import_shipment.provider.email,
                "phone": import_shipment.provider.phone,
                "telephone": import_shipment.provider.telephone,
            },
            "business_name": import_shipment.business.name,
            "type_id": import_shipment.type_id,
            "incoterm_code": import_shipment.incoterm.code,
            "port_name": import_shipment.port.name.title(),
            "status_id": import_shipment.status_id,
            "status_name": import_shipment.status.name,
            "local_agent_name": import_shipment.local_agent_name.title() if import_shipment.local_agent_name else None,
            "origin_agent_name": import_shipment.origin_agent_name.title() if import_shipment.origin_agent_name else None,
            "dates": {
                "booking": format_date(import_shipment.booking_date),
                "etd": format_date(import_shipment.etd_date),
                "eta": format_date(import_shipment.eta_date),
                "deadline": format_date(import_shipment.deadline_date),
                "pay": format_date(import_shipment.pay_date),
            },
            "cargo_details": {
                "qty": import_shipment.qty,
                "pallets": import_shipment.pallets,
                "weight": import_shipment.weight,
                "volume": import_shipment.volume,
            },
            "traffic_light": import_shipment.traffic_light,
            "delivery": {
                "date": format_date(import_shipment.delivery_date),
                "time": format_time(import_shipment.delivery_time),
                "name": import_shipment.delivery_name,
                "phone": import_shipment.delivery_phone,
                "code": import_shipment.delivery_code,
            },
            "chats": []
        }

        for chat in import_shipment.chats:
            order_data["chats"].append({
                "id": chat.id,
                "comment": chat.comment,
                "commenter_id": chat.commenter_id,
                "commenter_name": format_name(chat.commenter.name),
                "commenter_image": chat.commenter.image,
                "created_at": format_datetime(chat.created_at),
            })
            

        attachments, arc = self.import_repository.get_attachments_by_import(import_id)
        if arc != 200:
            return attachments, arc

        target_labels = {
            "consolidated": "Documentos consolidados",
            "product_list": "Lista de productos",
            "invoice": "Invoice",
            "packing_list": "Packing List",
            "certificate": "Constancia",
            "coo": "COO",
            "arrive": "Documentos de llegada",
            "invoices": "Facturas",
            "default": "Archivos",
        }

        grouped = {}
        for r in attachments:
            key = (r.target or "default").strip() or "default"
            grouped.setdefault(key, []).append(self._serialize_attachment(r))

        ordered_targets = [
            "consolidated",
            "product_list",
            "invoice",
            "packing_list",
            "certificate",
            "coo",
            "arrive",
            "invoices",
            "default",
        ]

        attachment_sections = []
        for target in ordered_targets:
            files = grouped.get(target, [])
            if files:
                attachment_sections.append({
                    "target": target,
                    "label": target_labels.get(target, target.replace("_", " ").title()),
                    "files": files
                })

        for target, files in grouped.items():
            if target not in ordered_targets and files:
                attachment_sections.append({
                    "target": target,
                    "label": target_labels.get(target, target.replace("_", " ").title()),
                    "files": files
                })

        order_data["attachment_sections"] = attachment_sections
        
        
        return order_data, 200
    

    @handle_exceptions
    def new(self, data):
        user_id = int(get_jwt_identity())

        provider_id = data.get("provider_id")
        business_id = data.get("business_id")
        type_id = data.get("type_id")
        incoterm_id = data.get("incoterm_id")
        port_id = data.get("port_id")
        local_agent = data.get("local_agent", "").strip()
        origin_agent = data.get("origin_agent", "").strip()

        if not provider_id:
            return "Selecciona un proveedor", 400
        if not business_id:
            return "Selecciona una empresa", 400
        if not type_id:
            return "Selecciona un tipo", 400
        if not incoterm_id:
            return "Selecciona un Incoterm", 400
        if not port_id:
            return "Selecciona un puerto", 400
        if not local_agent:
            return "Ingresa un agente local", 400
        if not origin_agent:
            return "Ingresa un agente de origen", 400

        import_id, ncc = self.import_repository.new_import(data)
        if ncc != 200:
            return import_id, ncc

        new_history, nhc = self.import_repository.new_history(import_id, user_id, 0, "Agregado a borrador")
        if nhc != 200:
            return new_history, nhc

        socketio.emit("imports_dashboard_update", {})

        return "Registrado correctamente", 200
    

    @handle_exceptions
    def move(self, data):
        user_id = int(get_jwt_identity())
        import_id = data.get("import_id")
        notes = data.get("notes")
        
        import_shipment, isc = self.import_repository.get_import(import_id) 
        if isc != 200:
            return import_shipment, isc

        current_status_id = import_shipment.status_id
        move, mc = self.import_repository.move_status(import_shipment, current_status_id, data) 
        if mc != 200:
            return move, mc
        
        new_history, nhc = self.import_repository.new_history(import_id, user_id, current_status_id, notes) 
        if nhc != 200:
            return new_history, nhc


        socketio.emit("imports_dashboard_update", {})
        return "Reclamo actualizado correctamente", 200


    @handle_exceptions
    def down(self, data):
        user_id = int(get_jwt_identity())
        import_id = data.get("import_id")
        
        import_shipment, isc = self.import_repository.get_import(import_id) 
        if isc != 200:
            return import_shipment, isc

        current_status_id = import_shipment.status_id
        move, mc = self.import_repository.move_status(import_shipment, current_status_id, data, down=True) 
        if mc != 200:
            return move, mc
        
        new_history, nhc = self.import_repository.new_history(import_id, user_id, current_status_id, down=True) 
        if nhc != 200:
            return new_history, nhc

        socketio.emit("imports_dashboard_update", {})
        return "Reclamo actualizado correctamente", 200
    
    
    def attachments_list(self, import_id):
        target = (request.args.get("target") or "default").strip()

        attachments, rc = self.import_repository.get_attachments(import_id, target)
        if rc != 200:
            return attachments, rc

        data = []
        for r in attachments:
            data.append({
                "id": r.id,
                "target": r.target,
                "original_name": r.original_name,
                "mime_type": r.mime_type,
                "size_bytes": r.size_bytes,
                "size_h": size(r.size_bytes),
                "created_at": str(r.created_at),
                "ext": file_extension(r.original_name),

                "inline_url": f"/imports/attachment/{r.id}?disposition=inline",
                "download_url": f"/imports/attachment/{r.id}?disposition=attachment",
                "preview_url": f"/imports/attachment/{r.id}/preview",
            })

        return {"data": data}, 200


    def attachments_upload(self):
        user_id = int(get_jwt_identity())

        import_id = request.form.get("import_id")
        target = (request.form.get("target") or "default").strip()
        files = request.files.getlist("files[]")
        if not files:
            return {"data": {"message": "No files received"}}, 400

        max_bytes = Paths.MAX_BYTES
        saved_ids = []

        for f in files:
            if not f or not f.filename:
                continue

            if not allowed_extension(f.filename):
                return {"data": {"message": f"File type not allowed: {f.filename}"}}, 400

            size = None
            try:
                pos = f.stream.tell()
                f.stream.seek(0, os.SEEK_END)
                size = f.stream.tell()
                f.stream.seek(pos)
            except Exception:
                pass

            if size is not None and size > max_bytes:
                return {"data": {"message": f"File too large (max {max_bytes} bytes): {f.filename}"}}, 400

            original_name = f.filename
            ext = file_extension(original_name)
            safe = secure_filename(original_name) or f"file.{ext}"
            stored_name = f"{uuid.uuid4().hex}_{safe}"

            path = os.path.join(upload_path(Paths.IMPORTS), stored_name)
            f.save(path)

            mime = getattr(f, "mimetype", None)
            size_bytes = os.path.getsize(path)

            new_id, nc = self.import_repository.add_attachment(
                import_id=import_id,
                user_id=user_id,
                target=target,
                original_name=original_name,
                stored_name=stored_name,
                mime_type=mime,
                size_bytes=size_bytes,
            )
            if nc != 200:
                return new_id, nc

            saved_ids.append(new_id)

        return {"data": {"uploaded": saved_ids}}, 200


    def attachment_stream(self, attachment_id, disposition="inline"):
        row, rc = self.import_repository.get_attachment_by_id(int(attachment_id))
        if rc != 200:
            return row, rc

        path = os.path.join(Paths.IMPORTS, row.stored_name)
        if not os.path.exists(path):
            return "File missing on disk", 404

        as_attachment = (disposition == "attachment")
        return send_file(
            path,
            mimetype=row.mime_type or "application/octet-stream",
            as_attachment=as_attachment,
            download_name=row.original_name
        )


    def _file_ext(self, filename):
        return (filename.rsplit(".", 1)[-1] if "." in filename else "").lower()
    

    # GET /complaint/attachment/<attachment_id>/preview
    def attachment_preview(self, attachment_id):
        row, rc = self.import_repository.get_attachment_by_id(int(attachment_id))
        if rc != 200:
            return row, rc

        ext = self._file_ext(row.original_name)
        inline_url = f"/imports/attachment/{row.id}?disposition=inline"

        if ext in {"png","jpg","jpeg","webp","gif","pdf"}:
            return {"kind": "url", "url": inline_url, "name": row.original_name}, 200

        path = os.path.join(Paths.IMPORTS, row.stored_name)
        if not os.path.exists(path):
            return "File missing on disk", 404

        if ext in {"txt","xml"}:
            with open(path, "r", encoding="utf-8", errors="replace") as fp:
                text = fp.read(200_000)
            return {"kind": "text", "text": text, "name": row.original_name}, 200

        if ext == "docx" and Document:
            doc = Document(path)
            parts = [p.text for p in doc.paragraphs if p.text]
            text = "\n".join(parts)[:200_000]
            return {"kind": "text", "text": text, "name": row.original_name}, 200

        if ext == "xlsx" and openpyxl:
            wb = openpyxl.load_workbook(path, data_only=True)
            ws = wb.active
            max_rows = min(ws.max_row or 0, 50)
            max_cols = min(ws.max_column or 0, 20)

            rows_html = []
            for r in range(1, max_rows + 1):
                cols = []
                for c in range(1, max_cols + 1):
                    v = ws.cell(row=r, column=c).value
                    cols.append(f"<td>{'' if v is None else str(v)}</td>")
                rows_html.append("<tr>" + "".join(cols) + "</tr>")

            html = "<table>" + "".join(rows_html) + "</table>"
            return {"kind": "html", "html": html, "name": row.original_name}, 200

        return {
            "kind": "download",
            "name": row.original_name,
            "message": "Vista previa no disponible",
            "download_url": f"/complaint/attachment/{row.id}?disposition=attachment"
        }, 200


    @handle_exceptions
    def chat(self, data):
        import_id = data.get("import_id")
        if not import_id:
            return "import_id requerido", 400

        comment = (data.get("comment") or "").strip()
        if not comment:
            return "Comentario vacío", 400

        current_user_id = int(get_jwt_identity())
        user, uc = self.user_repository.get_user_by_id(current_user_id)
        if uc != 200:
            return user, uc
        
        user_name = user.name

        import_data, idc = self.import_repository.get_import(import_id)
        if idc != 200:
            return import_data, idc

        chat, cc = self.import_repository.add_chat(import_id=import_id, user_id=current_user_id, comment=comment)
        if cc != 200:
            return chat, cc

        participants, _ = self.import_repository.get_chat_participants(import_id=import_id, exclude_user_id=current_user_id)
        
        title = f"Nuevo mensaje, importación SP-{import_id}"
        body = f"{format_name(user_name, True)}: {comment}"

        registration_tokens, users_without = self.push_service.prefetch_registration_tokens(participants)

        socketio.start_background_task(self.push_service.send_to_tokens, registration_tokens, title, body, None)
        socketio.start_background_task(socketio.emit, "complaint_dashboard_update", {})

        if users_without:
            logging.info(f"[FCM] users_without_tokens={users_without}")

        return {
            "id": chat.id,
            "comment": chat.comment,
            "commenter_id": chat.commenter_id,
            "commenter_name": format_name(chat.commenter.name),
            "commenter_image": chat.commenter.image,
            "created_at": format_datetime(chat.created_at),
        }, 200