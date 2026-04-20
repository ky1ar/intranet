import logging
from application.handlers import handle_logs_and_exceptions, validate_request
from application.services.attendance_service import AttendanceService


class AttendanceController:
    def __init__(self):
        self.attendance_service = AttendanceService() 


    @handle_logs_and_exceptions
    def attendance_xls(self, req):
        file = req.files.get("file")

        if not file or not file.filename:
            return "Missing file", 400

        file_bytes = file.read()
        if not file_bytes:
            return "Empty file", 400

        return self.attendance_service.xls_process(file, file_bytes)
    
    
    @handle_logs_and_exceptions
    def attendance_duration(self):
        return self.attendance_service.duration()
    

    @handle_logs_and_exceptions
    def attendance_leave(self):
        return self.attendance_service.leave()


    @handle_logs_and_exceptions
    def attendance_department_team(self, user_id):
        return self.attendance_service.get_department_team(user_id)


    @handle_logs_and_exceptions
    def attendance_get_leave(self, purchase_id):
        return self.attendance_service.get_leave(purchase_id)
    

    @handle_logs_and_exceptions
    def attendance_leave_requests(self):
        return self.attendance_service.leave_requests()
    
    
    @handle_logs_and_exceptions
    def summary_by_offset(self, data):
        return self.attendance_service.summary_by_offset(data)
    

    @handle_logs_and_exceptions
    def complete_marks(self, data):
        if validation_error := validate_request(data, {"user_id", "date", "additions"}):
            return validation_error, 422
        return self.attendance_service.complete_marks(data)


    @handle_logs_and_exceptions
    def leave_request(self, data):
        if validation_error := validate_request(data, {
            "user_id", "start_date", "type"
        }):
            return validation_error, 422
        return self.attendance_service.leave_request(data)
    

    @handle_logs_and_exceptions
    def leave_update(self, data):
        return self.attendance_service.leave_update(data)


    @handle_logs_and_exceptions
    def salary_calculate_stats(self, data):
        return self.attendance_service.salary_calculate_stats(
            data.get("period_id"),
            data.get("editor_user_id"),
        )
    

    @handle_logs_and_exceptions
    def salary_calculate(self, data):
        return self.attendance_service.salary_calculate(
            data.get("period_id"),
            data.get("editor_user_id"),
        )


    @handle_logs_and_exceptions
    def salary_recalculate_single(self, data):
        return self.attendance_service.salary_recalculate_single(
            data.get("salary_id"),
            data.get("editor_user_id"),
        )


    @handle_logs_and_exceptions
    def salary_get_period(self, period_id):
        return self.attendance_service.salary_get_period(period_id)


    @handle_logs_and_exceptions
    def salary_get_user(self, data):
        return self.attendance_service.salary_get_user(data)


    @handle_logs_and_exceptions
    def salary_config_save(self, data):
        return self.attendance_service.salary_config_save(data)


    @handle_logs_and_exceptions
    def salary_config_get(self, user_id):
        return self.attendance_service.salary_config_get(user_id)


    @handle_logs_and_exceptions
    def bank_account_get(self, user_id):
        return self.attendance_service.bank_account_get(user_id)

    @handle_logs_and_exceptions
    def bank_account_save(self, data):
        return self.attendance_service.bank_account_save(data)

    @handle_logs_and_exceptions
    def salary_approve_rrhh(self, data):
        return self.attendance_service.salary_approve_rrhh(
            data.get("salary_id"),
            data.get("approved_by"),
        )


    @handle_logs_and_exceptions
    def salary_approve_mgr(self, data):
        return self.attendance_service.salary_approve_mgr(
            data.get("salary_id"),
            data.get("approved_by"),
        )


    @handle_logs_and_exceptions
    def salary_set_factor(self, data):
        return self.attendance_service.salary_set_factor(
            data.get("salary_id"),
            data.get("factor"),
        )


    @handle_logs_and_exceptions
    def salary_set_adjustment(self, data):
        return self.attendance_service.salary_set_adjustment(
            data.get("salary_id"),
            data.get("adjustment"),
            data.get("adjusted_by"),
        )


    @handle_logs_and_exceptions
    def salary_generate_file(self, data):
        return self.attendance_service.salary_generate_telecredito(
            data.get("period_id"),
            data.get("business_id"),
        )

    @handle_logs_and_exceptions
    def salary_generate_bbva_cash(self, data):
        period_id = data.get("period_id")
        business_id = data.get("business_id")
        if not period_id or not business_id:
            return "period_id y business_id requeridos", 400
        return self.attendance_service.salary_generate_bbva_cash(period_id, business_id)


    # ── Leave Balance ──────────────────────────────────────────────────

    @handle_logs_and_exceptions
    def leave_balance_get(self, data):
        return self.attendance_service.get_leave_balance_for_user(
            data.get("user_id"),
            data.get("period_id"),
        )


    @handle_logs_and_exceptions
    def leave_balance_adjust(self, data):
        return self.attendance_service.set_leave_manual_adj(
            data.get("user_id"),
            data.get("period_id"),
            data.get("manual_adj"),
            data.get("adjusted_by"),
        )


    # ── Medical Leave (Descanso Médico) ────────────────────────────────

    @handle_logs_and_exceptions
    def medical_leave_request(self, req):
        return self.attendance_service.medical_leave_request(req)


    @handle_logs_and_exceptions
    def get_leave_attachments(self, leave_id):
        return self.attendance_service.get_leave_attachments(leave_id)

    @handle_logs_and_exceptions
    def add_leave_attachments(self, req):
        return self.attendance_service.add_leave_attachments(req)


    def get_leave_attachment_file(self, attachment_id, disposition="inline"):
        return self.attendance_service.get_leave_attachment_file(attachment_id, disposition)


    @handle_logs_and_exceptions
    def attachment_preview(self, attachment_id):
        return self.attendance_service.attachment_preview(attachment_id)

    @handle_logs_and_exceptions
    def delete_leave_attachment(self, attachment_id):
        return self.attendance_service.delete_leave_attachment(attachment_id)