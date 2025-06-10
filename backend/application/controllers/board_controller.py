import logging

from application.handlers import handle_logs_and_exceptions, validate_request
from application.services.board_service import BoardService


class BoardController:
    def __init__(self):
        self.board = BoardService() 


    @handle_logs_and_exceptions
    def board_dashboard(self, department_id):
        return self.board.dashboard(int(department_id))
    

    @handle_logs_and_exceptions
    def board_issue_add(self, data):
        if validation_error := validate_request(data, {"reporter_id", "title", "description"}):
            return validation_error, 422

        title = data.get("title", "").strip()
        if not title:
            return "Ingresa un título", 422
        return self.board.issue_add(data)
    

    @handle_logs_and_exceptions
    def board_issue_update(self, data):
        return self.board.issue_update(data)
    

    @handle_logs_and_exceptions
    def board_issue_delete(self, data):
        if validation_error := validate_request(data, {"issue_id"}):
            return validation_error, 422

        return self.board.issue_delete(data)
    

    @handle_logs_and_exceptions
    def board_issue_data(self, issue_id):
        return self.board.issue_data(issue_id)
    

    @handle_logs_and_exceptions
    def board_issue_status(self, data):
        if validation_error := validate_request(data, {"issue_id", "status_id"}):
            return validation_error, 422

        return self.board.issue_status(data)