import logging

from application.handlers import handle_exceptions
from application.utils import format_name
from application.repository.common_repository import CommonRepository


class CommonService:
    def __init__(self):
        self.common_repository = CommonRepository() 


    @handle_exceptions
    def vendors(self):
        vendors, vc = self.common_repository.get_vendors() 
        if vc != 200:
            return vendors, vc
        
        result = []
        for vendor in vendors:
            result.append({
                "id": vendor.id,
                "name": format_name(vendor.name)
            })
        return result, 200
    

    @handle_exceptions
    def workers(self):
        workers, wc = self.common_repository.get_workers() 
        if wc != 200:
            return workers, wc
        
        result = []
        for worker in workers:
            result.append({
                "id": worker.id,
                "name": format_name(worker.name)
            })
        return result, 200
    

    @handle_exceptions
    def departments(self):
        departments, dc = self.common_repository.get_departments() 
        if dc != 200:
            return departments, dc
        
        result = []
        for item in departments:
            result.append({
                "id": item.id,
                "name": item.name
            })
        return result, 200

    
    @handle_exceptions
    def provinces(self, department_id):
        provinces, pc = self.common_repository.get_provinces(department_id) 
        if pc != 200:
            return provinces, pc
        
        result = []
        for item in provinces:
            result.append({
                "id": item.id,
                "name": item.name
            })
        return result, 200
    

    @handle_exceptions
    def districts(self, province_id):
        districts, dc = self.common_repository.get_districts(province_id) 
        if dc != 200:
            return districts, dc
        
        result = []
        for item in districts:
            result.append({
                "id": item.id,
                "name": item.name
            })
        return result, 200
    