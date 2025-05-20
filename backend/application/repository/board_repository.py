import logging

from datetime import date, datetime, timezone, timedelta
from application.handlers import handle_db_exceptions
from application.models import BoardIssues, BoardHistory, Users
from sqlalchemy import desc
from flask import g


class BoardRepository:
    @handle_db_exceptions
    def get_board(self, department_id):
        department_id = int(department_id)
        query = g.db_session.query(BoardIssues)

        if department_id != 7:
            query = query.join(BoardIssues.assignee).filter(Users.department_id == department_id)

        board = query.order_by(BoardIssues.priority_id, desc(BoardIssues.id)).all()

        if not board:
            return [
                { "issues": [], "status_id": 1, "status_name": "Por hacer" },
                { "issues": [], "status_id": 2, "status_name": "En curso" },
                { "issues": [], "status_id": 3, "status_name": "Bloqueado" },
                { "issues": [], "status_id": 4, "status_name": "Listo" }
            ], 404

        return board, 200


    @handle_db_exceptions
    def add_issue(self, data):
        utc_now = datetime.now(timezone.utc)
        peru_time = utc_now - timedelta(hours=5)

        new_issue = BoardIssues(
            status_id=1,
            priority_id=data.get("priority_id", 3),
            reporter_id=data.get("reporter_id"),
            assignee_id=data.get("assignee_id"),
            type_id=1,
            title=data.get("title"),
            description=data.get("description"),
            created_at=peru_time,
        )

        g.db_session.add(new_issue)
        g.db_session.flush()
        g.db_session.commit()
        return new_issue.id, 200


    @handle_db_exceptions
    def add_history(self, issue_id, type, data):
        utc_now = datetime.now(timezone.utc)
        peru_time = utc_now - timedelta(hours=5)

        new_history = BoardHistory(
            user_id=data.get("reporter_id"),
            issue_id=issue_id,
            type=type,
            data=data,
            created_at=peru_time,
        )

        g.db_session.add(new_history)
        g.db_session.commit()
        return "Agregado correctamente", 200
    

    @handle_db_exceptions
    def get_issue(self, issue_id):
        board = (
            g.db_session.query(BoardIssues)
            .filter(BoardIssues.id == issue_id)
            .first()
        )
        if not board:
            return 'Tarea no localizada', 404

        return board, 200
    

    @handle_db_exceptions
    def update_issue(self, issue, data):
        utc_now = datetime.now(timezone.utc)
        peru_time = utc_now - timedelta(hours=5)
        
        if "assignee_id" in data:
            issue.assignee_id = data.get("assignee_id")

        if "title" in data:
            issue.title = data.get("title")

        if "description" in data:
            issue.description = data.get("description")

        if "priority_id" in data:
            issue.priority_id = data.get("priority_id")
        
        if "status_id" in data:
            issue.status_id = data.get("status_id")

        issue.updated_at = peru_time

        g.db_session.add(issue)
        g.db_session.flush()
        g.db_session.commit()
        return "Tarea actualizada correctamente.", 200
    

    @handle_db_exceptions
    def delete_issue(self, issue):
        g.db_session.delete(issue)
        g.db_session.commit()
        return "Tarea actualizada correctamente.", 200