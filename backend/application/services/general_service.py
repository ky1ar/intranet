import logging, requests, os

from datetime import datetime, timedelta
from application.handlers import handle_exceptions
from application.repository.general_repository import GeneralRepository
from flask import g


class GeneralService:
    def __init__(self):
        self.repository = GeneralRepository() 


    @handle_exceptions
    def service_status(self):
        service_status, service_order_status = self.repository.get_service_status() 
        if service_order_status != 200:
            return service_status, service_order_status
        
        result = {
            status.id: {
                "name": status.name,
                "image": status.image,
            }
            for status in service_status
        }
        return result, 200
    

    @handle_exceptions
    def service_methods(self):
        service_methods, methods_status = self.repository.get_service_methods() 
        if methods_status != 200:
            return service_methods, methods_status
        
        result = [
            {   
                "id": method.id,
                "name": method.name,
            }
            for method in service_methods
        ]
        return result, 200


    @handle_exceptions
    def get_technicians(self):
        technicians, technicians_status = self.repository.get_technicians() 
        if technicians_status != 200:
            return technicians, technicians_status
        
        return [technician.to_dict(only_fields=['id', 'name']) for technician in technicians], 200
    

    @handle_exceptions
    def get_tracking_agencies(self):
        agencies, agencies_status = self.repository.get_agencies() 
        if agencies_status != 200:
            return agencies, agencies_status
        
        result = [
            {
                "id": agency.id,
                "name": agency.name,
                "image": agency.image,
            }
            for agency in agencies
        ]
        return result, 200
    
        
