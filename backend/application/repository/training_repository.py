from application.handlers import handle_db_exceptions
from application.models import TrainingCalendar
from flask import g


class TrainingRepository:
    @handle_db_exceptions
    def get_calendar(self, first_day, last_day):
        calendar = (
            g.db_session.query(TrainingCalendar)
            .filter(TrainingCalendar.training_date >= first_day, TrainingCalendar.training_date <= last_day)
            .all()
        )

        if not calendar:
            return {}, 200

        grouped_calendar = {}
        for training in calendar:
            training_date = training.training_date
            if training_date not in grouped_calendar:
                grouped_calendar[training_date] = []
            grouped_calendar[training_date].append(training)

        return grouped_calendar, 200
        