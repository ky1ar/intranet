import logging
from application.handlers import handle_logs_and_exceptions
from application.services.module_service import ModuleService


class ModuleController:
    def __init__(self):
        self.module = ModuleService()


    @handle_logs_and_exceptions
    def get_my_modules(self, user_id):
        return self.module.get_user_modules(user_id)


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