import logging
from application.handlers import handle_exceptions
from application.repository.module_repository import ModuleRepository
from application import socketio
from flask_jwt_extended import get_jwt_identity


class ModuleService:
    def __init__(self):
        self.module_repository = ModuleRepository()


    def _current_user_id(self):
        try:
            return int(get_jwt_identity())
        except Exception:
            return None


    def _emit_permissions_update(self, user_id):
        """Emite evento para que el front recargue permisos sin F5"""
        modules, rc = self.get_user_modules(user_id)
        default_page, _ = self.get_default_page(user_id)

        payload = {
            "user_id": user_id,
            "default_page": default_page,
            "modules": modules if isinstance(modules, list) else [],
        }
        socketio.emit("modules_updated", payload)


    @handle_exceptions
    def get_user_modules(self, user_id):
        access_list, ac = self.module_repository.get_user_access(user_id)
        if ac != 200:
            return access_list, ac

        all_permissions, pc = self.module_repository.get_user_granted_permissions(user_id)
        if pc != 200:
            return all_permissions, pc

        perm_map = {}
        for up in all_permissions:
            mid = up.permission.module_id
            if mid not in perm_map:
                perm_map[mid] = {}
            perm_map[mid][up.permission.slug] = True

        modules = []
        for acc in access_list:
            m = acc.module
            granted = perm_map.get(m.id, {})

            permissions = {}
            for mp in m.permissions:
                permissions[mp.slug] = granted.get(mp.slug, False)

            modules.append({
                "slug": m.slug,
                "name": m.name,
                "icon": m.icon,
                "is_default": acc.is_default,
                "is_pinned": acc.is_pinned,
                "sort_order": acc.user_sort_order,
                "permissions": permissions,
            })

        return modules, 200


    @handle_exceptions
    def get_default_page(self, user_id):
        access, ac = self.module_repository.get_user_default_module(user_id)
        if ac != 200:
            return "logistics", 200

        if access:
            return access.module.slug, 200

        return "logistics", 200


    @handle_exceptions
    def set_default_module(self, user_id, module_slug):
        module, mc = self.module_repository.get_module_by_slug(module_slug)
        if mc != 200:
            return module, mc

        return self.module_repository.set_default_module(user_id, module.id)


    @handle_exceptions
    def update_sort_order(self, user_id, order_list):
        return self.module_repository.update_user_sort_order(user_id, order_list)


    @handle_exceptions
    def toggle_pin(self, user_id, module_slug):
        module, mc = self.module_repository.get_module_by_slug(module_slug)
        if mc != 200:
            return module, mc

        result, rc = self.module_repository.toggle_pin(user_id, module.id)
        if rc != 200:
            return result, rc

        return {"slug": module_slug, "is_pinned": result["is_pinned"]}, 200


    @handle_exceptions
    def check_permission(self, user_id, module_slug, permission_slug):
        module, mc = self.module_repository.get_module_by_slug(module_slug)
        if mc != 200:
            return False, 200

        perms, pc = self.module_repository.get_user_permissions_by_module(user_id, module.id)
        if pc != 200:
            return False, 200

        has = any(p.permission.slug == permission_slug for p in perms)
        return {"granted": has}, 200


    # ── Admin ──────────────────────────────────────────────────────────────

    @handle_exceptions
    def get_all_modules(self):
        return self.module_repository.get_all_active_modules()


    @handle_exceptions
    def set_user_access(self, user_id, module_slug, visible, is_pinned=True):
        module, mc = self.module_repository.get_module_by_slug(module_slug)
        if mc != 200:
            return module, mc

        result, rc = self.module_repository.upsert_user_access(
            user_id=user_id,
            module_id=module.id,
            visible=visible,
            is_pinned=is_pinned,
        )

        if rc == 200:
            self._emit_permissions_update(user_id)

        return result, rc


    @handle_exceptions
    def set_user_permissions(self, user_id, module_slug, permissions_dict):
        module, mc = self.module_repository.get_module_by_slug(module_slug)
        if mc != 200:
            return module, mc

        result, rc = self.module_repository.bulk_set_user_permissions(
            user_id=user_id,
            module_id=module.id,
            permissions_dict=permissions_dict,
        )

        if rc == 200:
            self._emit_permissions_update(user_id)

        return result, rc