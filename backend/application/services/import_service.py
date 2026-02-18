import logging, os, uuid
from datetime import date, datetime
from werkzeug.utils import secure_filename
from flask import request, send_file, render_template
from flask_jwt_extended import get_jwt_identity
from application.handlers import handle_exceptions
from application.utils import format_name, format_datetime, calculate_passed_days, format_date, size, file_extension, allowed_extension, upload_path
from application.repository.import_repository import ImportRepository
from application.repository.user_repository import UserRepository
from application.repository.client_repository import ClientRepository
from application.services.push_service import PushSender
from application import socketio
from config import Paths



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
            }

            result.append(order_data)
        return result, 200


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
                    "priority": 'low',
                    "updated_today": updated_today,
                    "passed_days": passed_days,
                    "status_id": status.id,
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