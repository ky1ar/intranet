import logging
from application.handlers import handle_exceptions
from application.repository.module_repository import ModuleRepository
from application.repository.user_repository import UserRepository
from application.utils import format_name
from flask_jwt_extended import get_jwt_identity
from application import socketio


class ModuleService:
    def __init__(self):
        self.module_repository = ModuleRepository()
        self.user_repository = UserRepository()


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
    def get_user_full_access_map(self, target_user_id, editor_user_id):
        editor, ec = self.user_repository.get_user_by_id(editor_user_id)
        if ec != 200:
            return editor, ec

        if editor.level_id < 3:
            return "Sin permisos para gestionar usuarios", 403

        target, tc = self.user_repository.get_user_by_id(target_user_id)
        if tc != 200:
            return target, tc

        if editor.level_id == 3 and target.level_id >= 3:
            return "No puedes gestionar a este usuario", 403

        target_map, rc = self.module_repository.get_user_full_access_map(target_user_id)
        if rc != 200:
            return target_map, rc

        # super puede todo
        if editor.level_id == 4:
            for mod in target_map:
                mod["can_edit"] = True
                for p in mod["permissions"]:
                    p["can_edit"] = True
            return target_map, 200

        # admin solo puede dar lo que él tiene
        editor_modules, _ = self.get_user_modules(editor_user_id)
        editor_slugs = {}
        if isinstance(editor_modules, list):
            for em in editor_modules:
                editor_slugs[em["slug"]] = em["permissions"]

        for mod in target_map:
            editor_perms = editor_slugs.get(mod["slug"], {})
            mod["can_edit"] = mod["slug"] in editor_slugs

            for p in mod["permissions"]:
                p["can_edit"] = editor_perms.get(p["slug"], False)

        return target_map, 200


    @handle_exceptions
    def get_manageable_users(self, editor_user_id):
        editor, ec = self.user_repository.get_user_by_id(editor_user_id)
        if ec != 200:
            return editor, ec

        if editor.level_id < 3:
            return "Sin permisos", 403

        users, uc = self.module_repository.get_manageable_users(editor.level_id, editor_user_id)
        if uc != 200:
            return users, uc

        result = []
        for u in users:
            result.append({
                "id": u.id,
                "name": format_name(u.name),
                "image": u.image if u.image else 'user_default.jpg',
                "level_id": u.level_id,
                "department_name": u.department.name if u.department else "",
            })

        return result, 200


    @handle_exceptions
    def save_user_permissions(self, editor_user_id, target_user_id, modules_data):
        editor, ec = self.user_repository.get_user_by_id(editor_user_id)
        if ec != 200:
            return editor, ec

        if editor.level_id < 3:
            return "Sin permisos", 403

        target, tc = self.user_repository.get_user_by_id(target_user_id)
        if tc != 200:
            return target, tc

        if editor.level_id == 3 and target.level_id >= 3:
            return "No puedes gestionar a este usuario", 403

        editor_modules_raw, _ = self.get_user_modules(editor_user_id)
        editor_slugs = {}
        if isinstance(editor_modules_raw, list):
            for em in editor_modules_raw:
                editor_slugs[em["slug"]] = em["permissions"]

        for mod_data in modules_data:
            slug = mod_data.get("slug")
            if not slug:
                continue

            module, mc = self.module_repository.get_module_by_slug(slug)
            if mc != 200:
                continue

            # admin solo puede tocar módulos que él tiene
            if editor.level_id == 3 and slug not in editor_slugs:
                continue

            self.module_repository.upsert_user_access(
                user_id=target_user_id,
                module_id=module.id,
                visible=mod_data.get("visible", False),
            )

            perms_dict = mod_data.get("permissions", {})
            if editor.level_id == 3:
                editor_perms = editor_slugs.get(slug, {})
                perms_dict = {
                    k: v for k, v in perms_dict.items()
                    if editor_perms.get(k, False)
                }

            if perms_dict:
                self.module_repository.bulk_set_user_permissions(
                    user_id=target_user_id,
                    module_id=module.id,
                    permissions_dict=perms_dict,
                )

        self._emit_permissions_update(target_user_id)
        return "Permisos guardados", 200
    

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
                "module_id": m.id,
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
    def save_my_settings(self, user_id, modules_data):
        if not modules_data:
            return "modules requerido", 400
        return self.module_repository.save_user_settings(user_id, modules_data)


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