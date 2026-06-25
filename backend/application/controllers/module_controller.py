import logging
from application.handlers import handle_logs_and_exceptions
from application.services.module_service import ModuleService


class ModuleController:
    def __init__(self):
        self.module = ModuleService()


    @handle_logs_and_exceptions
    def get_manageable_users(self, editor_user_id):
        return self.module.get_manageable_users(editor_user_id)


    @handle_logs_and_exceptions
    def get_user_access_map(self, data):
        editor_user_id = data.get('editor_user_id')
        target_user_id = data.get('target_user_id')

        if not target_user_id:
            return "target_user_id requerido", 400

        return self.module.get_user_full_access_map(target_user_id, editor_user_id)


    @handle_logs_and_exceptions
    def save_user_permissions(self, data):
        editor_user_id = data.get('editor_user_id')
        target_user_id = data.get('target_user_id')
        modules_data = data.get('modules', [])

        if not target_user_id or not modules_data:
            return "target_user_id y modules requeridos", 400

        return self.module.save_user_permissions(editor_user_id, target_user_id, modules_data)
    

    @handle_logs_and_exceptions
    def get_my_modules(self, user_id):
        return self.module.get_user_modules(user_id)


    @handle_logs_and_exceptions
    def save_my_settings(self, data):
        user_id = data.get('user_id')
        modules_data = data.get('modules', [])
        nav_order = data.get('nav_order')
        if not modules_data:
            return "modules requerido", 400
        return self.module.save_my_settings(user_id, modules_data, nav_order)


    @handle_logs_and_exceptions
    def set_default(self, data):
        user_id = data.get('user_id')
        module_slug = data.get('module_slug')

        if not module_slug:
            return "module_slug requerido", 400

        return self.module.set_default_module(user_id, module_slug)


    @handle_logs_and_exceptions
    def update_sort_order(self, data):
        user_id = data.get('user_id')
        order_list = data.get('order', [])

        if not order_list:
            return "order requerido", 400

        return self.module.update_sort_order(user_id, order_list)


    @handle_logs_and_exceptions
    def toggle_pin(self, data):
        user_id = data.get('user_id')
        module_slug = data.get('module_slug')

        if not module_slug:
            return "module_slug requerido", 400

        return self.module.toggle_pin(user_id, module_slug)


    # ── Admin ──────────────────────────────────────────────────────────────

    @handle_logs_and_exceptions
    def get_all_modules(self):
        return self.module.get_all_modules()


    @handle_logs_and_exceptions
    def set_user_access(self, data):
        user_id = data.get('user_id')
        module_slug = data.get('module_slug')
        visible = data.get('visible', False)
        is_pinned = data.get('is_pinned', True)

        if not user_id or not module_slug:
            return "user_id y module_slug requeridos", 400

        return self.module.set_user_access(user_id, module_slug, visible, is_pinned)


    @handle_logs_and_exceptions
    def set_user_permissions(self, data):
        user_id = data.get('user_id')
        module_slug = data.get('module_slug')
        permissions = data.get('permissions', {})

        if not user_id or not module_slug:
            return "user_id y module_slug requeridos", 400

        return self.module.set_user_permissions(user_id, module_slug, permissions)