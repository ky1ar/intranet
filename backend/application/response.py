import logging

logging.getLogger('python_http_client').setLevel(logging.WARNING)


class Response:
    def __init__(self):
        self.RESET = "\033[0m"
        self.RED = "\033[31m"
        self.GREEN = "\033[32m"
        self.YELLOW = "\033[33m"
        self.BLUE = "\033[34m"
        self.MAGENTA = "\033[35m"


    def success(self, data):
        if isinstance(data, str):
            data = {'message': data}

        app_version = None
        if isinstance(data, dict):
            app_version = data.pop("app_version", None)

        response = {
            "data": data,
            "success": True
        }

        if app_version:
            response["app_version"] = app_version

        logging.info(f"{self.GREEN}{response}{self.RESET}")
        return response, 200
    

    def error(self, data, code):
        if isinstance(data, str):
            data = {'message': data}
            
        response = {
            "data": data,
            "success": False
        }

        log_color = self.MAGENTA if code > 400 else self.RED
        logging.info(f"{log_color}{response}{self.RESET}")
        return response, code
