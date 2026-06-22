import logging
from functools import wraps
from flask import Response as respon
from application.response import Response
from sqlalchemy.exc import SQLAlchemyError
from flask import g


format = Response()

    
def get_internal_server_error():
    return 'Error interno del servidor', 500


def validate_request(request, required_keys):
    if not required_keys.issubset(request):
        missing_keys = required_keys - request.keys()
        logging.error(f'Missing keys on input data: {missing_keys}')
        return 'missing_key'
    return None


def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Exception in {func.__name__}: {e}", exc_info=True)
            return get_internal_server_error()
    return wrapper


def handle_db_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SQLAlchemyError as e:
            g.db_session.rollback()
            logging.exception(f"Database error in {func.__name__}: {e}")
            return get_internal_server_error()
        except Exception as e:
            logging.error(f"Exception in {func.__name__}: {e}", exc_info=True)
            return get_internal_server_error()
        finally:
            g.db_session.close()
    return wrapper


def handle_logs_and_exceptions(method):
    @wraps(method)
    def wrapper(self, request=None):
        method_name = method.__name__
        try:
            logging.debug('-----------------------------------------------------------------------\n\n')
            logging.debug(f'------------------------- {method_name.capitalize()} --------------------------')
            if request:
                logging.info(f"{format.YELLOW}{request}{format.RESET}")

            result = method(self, request) if request is not None else method(self)

            if isinstance(result, respon):
                return result

            response, response_code = result
            if response_code != 200:
                return format.error(response, response_code)
            return format.success(response)

        except Exception as e:
            logging.error(f"Exception in {method_name}: {e}", exc_info=True)
            return format.error(str(e), 500)

    return wrapper