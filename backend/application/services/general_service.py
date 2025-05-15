import logging

from application.handlers import handle_exceptions
from application.repository.general_repository import GeneralRepository


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
        
        result = []
        for technician in technicians:
            name = self.format_name(technician.name)
            result.append({
                "id": technician.id,
                "name": name
            })
        return result, 200
    

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
    
    
    @handle_exceptions
    def get_tracking_status(self):
        tracking_status, tracking_code = self.repository.get_tracking_status() 
        if tracking_code != 200:
            return tracking_status, tracking_code
        
        result = [
            {
                "id": status.id,
                "name": status.name,
            }
            for status in tracking_status
        ]
        return result, 200
    

    @handle_exceptions
    def get_drivers(self):
        drivers, drivers_status = self.repository.get_drivers() 
        if drivers_status != 200:
            return drivers, drivers_status
        
        result = []
        for driver in drivers:
            name = self.format_name(driver.name)
            result.append({
                "id": driver.id,
                "name": name
            })
        return result, 200
    

    @handle_exceptions
    def get_vendors(self):
        vendors, vendors_status = self.repository.get_vendors() 
        if vendors_status != 200:
            return vendors, vendors_status
        
        result = []
        for vendor in vendors:
            name = self.format_name(vendor.name)
            result.append({
                "id": vendor.id,
                "name": name
            })
        return result, 200
    

    @handle_exceptions
    def get_districts(self):
        districts, districts_status = self.repository.get_districts() 
        if districts_status != 200:
            return districts, districts_status
        
        districts_data = [district.to_dict() for district in districts]
        #redis_client.setex(cache_key, 86400, json.dumps(districts_data)) #86400 dia #3600 hora #300 5

        return districts_data, 200


    @handle_exceptions
    def get_shipping_types(self):
        shipping_types, shipping_types_status = self.repository.get_shipping_types() 
        if shipping_types_status != 200:
            return shipping_types, shipping_types_status
        
        data = [shipping_type.to_dict() for shipping_type in shipping_types]

        return data, 200
    

    @handle_exceptions
    def format_name(self, full_name):
        words = full_name.strip().split()

        if len(words) == 3:
            return f"{words[0]} {words[1]}"
        elif len(words) == 4:
            return f"{words[0]} {words[2]}"
        elif len(words) == 5:
            return f"{words[0]} {words[3]}"
        return "Texto no válido"
        
