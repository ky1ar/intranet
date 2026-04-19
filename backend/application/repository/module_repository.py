import logging
from datetime import datetime, timezone, timedelta
from application.models import Users
from application.db_models.module_model import Module, ModulePermission, UserModuleAccess, UserModulePermission
from application.handlers import handle_db_exceptions
from application.utils import peru_time
from flask import g


class ModuleRepository:
    @handle_db_exceptions
    def get_user_full_access_map(self, user_id):
        modules = (
            g.db_session.query(Module)
            .filter(Module.is_active == True)
            .filter(Module.slug != 'admin')
            .order_by(Module.sort_order)
            .all()
        )

        access_map = {}
        access_rows = (
            g.db_session.query(UserModuleAccess)
            .filter(UserModuleAccess.user_id == user_id)
            .all()
        )
        for a in access_rows:
            access_map[a.module_id] = a

        perm_rows = (
            g.db_session.query(UserModulePermission)
            .filter(UserModulePermission.user_id == user_id)
            .all()
        )
        perm_map = {}
        for p in perm_rows:
            perm_map[p.module_permission_id] = p.granted

        result = []
        for m in modules:
            acc = access_map.get(m.id)
            perms = []
            for mp in m.permissions:
                perms.append({
                    "id": mp.id,
                    "slug": mp.slug,
                    "name": mp.name,
                    "granted": perm_map.get(mp.id, False),
                })

            result.append({
                "module_id": m.id,
                "slug": m.slug,
                "name": m.name,
                "icon": m.icon,
                "visible": acc.visible if acc else False,
                "is_pinned": acc.is_pinned if acc else True,
                "permissions": perms,
            })

        return result, 200


    @handle_db_exceptions
    def get_manageable_users(self, editor_level_id, editor_id):
        query = (
            g.db_session.query(Users)
            .filter(Users.level_id != 1)
            .filter(Users.level_id != 5)
            .filter(Users.document != "00000000")
        )

        if editor_id != 23:
            query = query.filter(Users.id != 23)
            query = query.filter(Users.id != editor_id)

        if editor_level_id == 3:
            query = query.filter(Users.level_id == 2)

        users = query.order_by(Users.name).all()
        return users, 200


    @handle_db_exceptions
    def get_all_active_modules(self):
        modules = (
            g.db_session.query(Module)
            .filter(Module.is_active == True)
            .order_by(Module.sort_order)
            .all()
        )
        return modules, 200


    @handle_db_exceptions
    def get_module_by_slug(self, slug):
        module = (
            g.db_session.query(Module)
            .filter(Module.slug == slug)
            .first()
        )
        if not module:
            return "Módulo no encontrado", 404
        return module, 200


    @handle_db_exceptions
    def get_user_access(self, user_id):
        access_list = (
            g.db_session.query(UserModuleAccess)
            .filter(
                UserModuleAccess.user_id == user_id,
                UserModuleAccess.visible == True
            )
            .order_by(UserModuleAccess.user_sort_order)
            .all()
        )
        return access_list, 200


    @handle_db_exceptions
    def get_user_default_module(self, user_id):
        access = (
            g.db_session.query(UserModuleAccess)
            .filter(
                UserModuleAccess.user_id == user_id,
                UserModuleAccess.visible == True,
                UserModuleAccess.is_default == True
            )
            .first()
        )
        return access, 200


    @handle_db_exceptions
    def get_user_granted_permissions(self, user_id):
        permissions = (
            g.db_session.query(UserModulePermission)
            .filter(
                UserModulePermission.user_id == user_id,
                UserModulePermission.granted == True
            )
            .all()
        )
        return permissions, 200


    @handle_db_exceptions
    def get_user_permissions_by_module(self, user_id, module_id):
        permissions = (
            g.db_session.query(UserModulePermission)
            .join(ModulePermission)
            .filter(
                UserModulePermission.user_id == user_id,
                ModulePermission.module_id == module_id,
                UserModulePermission.granted == True
            )
            .all()
        )
        return permissions, 200


    @handle_db_exceptions
    def set_default_module(self, user_id, module_id):
        (
            g.db_session.query(UserModuleAccess)
            .filter(
                UserModuleAccess.user_id == user_id,
                UserModuleAccess.is_default == True
            )
            .update({'is_default': False})
        )

        updated = (
            g.db_session.query(UserModuleAccess)
            .filter(
                UserModuleAccess.user_id == user_id,
                UserModuleAccess.module_id == module_id
            )
            .update({'is_default': True})
        )

        if not updated:
            return "El usuario no tiene acceso a este módulo", 404

        g.db_session.commit()
        return "Default actualizado", 200


    @handle_db_exceptions
    def save_user_settings(self, user_id, modules_data):
        (
            g.db_session.query(UserModuleAccess)
            .filter(UserModuleAccess.user_id == user_id)
            .update({'is_default': False})
        )

        for item in modules_data:
            (
                g.db_session.query(UserModuleAccess)
                .filter(
                    UserModuleAccess.user_id == user_id,
                    UserModuleAccess.module_id == item['module_id']
                )
                .update({
                    'user_sort_order': item['sort_order'],
                    'is_pinned': item['is_pinned'],
                    'is_default': item.get('is_default', False),
                })
            )

        g.db_session.commit()
        return "Configuración guardada", 200


    @handle_db_exceptions
    def update_user_sort_order(self, user_id, order_list):
        for item in order_list:
            (
                g.db_session.query(UserModuleAccess)
                .filter(
                    UserModuleAccess.user_id == user_id,
                    UserModuleAccess.module_id == item['module_id']
                )
                .update({'user_sort_order': item['sort_order']})
            )

        g.db_session.commit()
        return "Orden actualizado", 200


    @handle_db_exceptions
    def toggle_pin(self, user_id, module_id):
        access = (
            g.db_session.query(UserModuleAccess)
            .filter(
                UserModuleAccess.user_id == user_id,
                UserModuleAccess.module_id == module_id
            )
            .first()
        )

        if not access:
            return "Acceso no encontrado", 404

        access.is_pinned = not access.is_pinned
        access.updated_at = peru_time()
        g.db_session.commit()

        return {"is_pinned": access.is_pinned}, 200


    # ── Admin ──────────────────────────────────────────────────────────────

    @handle_db_exceptions
    def upsert_user_access(self, user_id, module_id, visible, is_pinned=True, user_sort_order=0):
        access = (
            g.db_session.query(UserModuleAccess)
            .filter(
                UserModuleAccess.user_id == user_id,
                UserModuleAccess.module_id == module_id
            )
            .first()
        )

        if not access:
            access = UserModuleAccess(
                user_id=user_id,
                module_id=module_id,
                visible=visible,
                is_pinned=is_pinned,
                user_sort_order=user_sort_order,
            )
            g.db_session.add(access)
        else:
            access.visible = visible
            access.is_pinned = is_pinned
            access.user_sort_order = user_sort_order
            access.updated_at = peru_time()

        g.db_session.commit()
        return access, 200


    @handle_db_exceptions
    def upsert_user_permission(self, user_id, module_permission_id, granted):
        perm = (
            g.db_session.query(UserModulePermission)
            .filter(
                UserModulePermission.user_id == user_id,
                UserModulePermission.module_permission_id == module_permission_id
            )
            .first()
        )

        if not perm:
            perm = UserModulePermission(
                user_id=user_id,
                module_permission_id=module_permission_id,
                granted=granted,
            )
            g.db_session.add(perm)
        else:
            perm.granted = granted
            perm.updated_at = peru_time()

        g.db_session.commit()
        return perm, 200


    @handle_db_exceptions
    def bulk_set_user_permissions(self, user_id, module_id, permissions_dict):
        module_perms = (
            g.db_session.query(ModulePermission)
            .filter(ModulePermission.module_id == module_id)
            .all()
        )

        perm_map = {mp.slug: mp.id for mp in module_perms}

        for slug, granted in permissions_dict.items():
            mp_id = perm_map.get(slug)
            if not mp_id:
                continue

            existing = (
                g.db_session.query(UserModulePermission)
                .filter(
                    UserModulePermission.user_id == user_id,
                    UserModulePermission.module_permission_id == mp_id
                )
                .first()
            )

            if not existing:
                g.db_session.add(UserModulePermission(
                    user_id=user_id,
                    module_permission_id=mp_id,
                    granted=granted,
                ))
            else:
                existing.granted = granted
                existing.updated_at = peru_time()

        g.db_session.commit()
        return "Permisos actualizados", 200