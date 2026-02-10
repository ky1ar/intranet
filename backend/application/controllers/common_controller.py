import logging

from application.handlers import handle_logs_and_exceptions, validate_request
from application.services.common_service import CommonService
from flask import g


class CommonController:
    def __init__(self):
        self.common = CommonService() 


    @handle_logs_and_exceptions
    def common_vendors(self):
        return self.common.vendors()
    

    @handle_logs_and_exceptions
    def common_workers(self):
        return self.common.workers()
    

    @handle_logs_and_exceptions
    def common_departments(self):
        return self.common.departments()
    

    @handle_logs_and_exceptions
    def common_provinces(self, department_id):
        return self.common.provinces(department_id)
    

    @handle_logs_and_exceptions
    def common_districts(self, province_id):
        return self.common.districts(province_id)
