import logging, json
from application import redis_client
from datetime import date, datetime, timezone, timedelta
from application.handlers import handle_exceptions
from application.repository.board_repository import BoardRepository
from application.repository.general_repository import GeneralRepository
from application.models import HistoryType
from application import socketio


class BoardService:
    def __init__(self):
        self.repository = BoardRepository()
        self.general = GeneralRepository()
        self.dias_semana = {
            0: 'lun.',
            1: 'mar.',
            2: 'mié.',
            3: 'jue.',
            4: 'vie.',
            5: 'sáb.',
            6: 'dom.'
        }

        self.meses = {
            1: 'enero',
            2: 'febrero',
            3: 'marzo',
            4: 'abril',
            5: 'mayo',
            6: 'junio',
            7: 'julio',
            8: 'agosto',
            9: 'septiembre',
            10: 'octubre',
            11: 'noviembre',
            12: 'diciembre'
        }
    
    @handle_exceptions
    def dashboard(self, department_id):
        board, board_status = self.repository.get_board(department_id)
        if board_status != 200:
            return board, board_status
        
        statuses, statuses_status = self.general.get_board_statuses()
        if statuses_status != 200:
            return statuses, statuses_status
        
        grouped = {
            status.id: {
                "status_id": status.id,
                "status_name": status.name,
                "issues": []
            }
            for status in statuses
        }

        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=4)
        
        for issue in board:
            if department_id == 7 and issue.assignee and issue.assignee.level_id == 5:
                continue

            if issue.status.id == 4:
                created_date = issue.updated_at.date()
                if not (start_of_week <= created_date <= end_of_week):
                    continue

            raw_date = issue.created_at.strftime("%d-%m-%Y")
            date_obj = datetime.strptime(raw_date, "%d-%m-%Y")
            dia_semana = self.dias_semana[date_obj.weekday()]
            mes = self.meses[date_obj.month]
            dia = date_obj.day

            grouped[issue.status.id]["issues"].append({
                "id": issue.id,
                "created_at": f"{dia_semana} {dia} de {mes}",
                "title": issue.title,
                "status_id": issue.status_id,
                "assignee_image": issue.assignee.image if issue.assignee and issue.assignee.image else 'user_default.jpg',
                "assignee_name": issue.assignee.name,
                "priority_id": issue.priority_id,
                "assignee_id": issue.assignee_id if issue.assignee_id else 0,
            })

        result = list(grouped.values())

        return result, 200


    @handle_exceptions
    def issue_add(self, data):
        issue, issue_status = self.repository.add_issue(data)
        if issue_status != 200:
            return issue, issue_status
        
        socketio.emit("update_board", {})
        return self.repository.add_history(issue, HistoryType.ADDED, data)
    

    @handle_exceptions
    def issue_update(self, data):
        issue_id = data.get("issue_id")
        issue, issue_status = self.repository.get_issue(issue_id)
        if issue_status != 200:
            return issue, issue_status
        
        update, update_status = self.repository.update_issue(issue, data)
        if update_status != 200:
            return update, update_status
        
        socketio.emit("update_board", {})
        return self.repository.add_history(issue_id, HistoryType.UPDATED, data)
    

    @handle_exceptions
    def issue_delete(self, data):
        issue_id = data.get("issue_id")
        issue, issue_status = self.repository.get_issue(issue_id)
        if issue_status != 200:
            return issue, issue_status
        
        delete, delete_status = self.repository.delete_issue(issue)
        if delete_status != 200:
            return delete, delete_status
        
        socketio.emit("update_board", {})
        return self.repository.add_history(issue_id, HistoryType.DELETED, data)


    @handle_exceptions
    def issue_data(self, issue_id):
        issue, issue_status = self.repository.get_issue(issue_id)
        if issue_status != 200:
            return issue, issue_status
        
        return issue.to_dict(), 200
    

    @handle_exceptions
    def issue_status(self, data):
        issue_id = data.get("issue_id")
        issue, issue_status = self.repository.get_issue(issue_id)
        if issue_status != 200:
            return issue, issue_status
        
        update, update_status = self.repository.update_issue(issue, data)
        if update_status != 200:
            return update, update_status
        socketio.emit("update_board", {})
        return self.repository.add_history(issue_id, HistoryType.STATUS_CHANGE, data)