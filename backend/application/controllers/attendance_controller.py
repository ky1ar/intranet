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