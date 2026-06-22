import logging, requests, os, calendar
from datetime import date, datetime, timezone, timedelta
from application.handlers import handle_exceptions
from application.utils import format_name, format_datetime

from application.repository.training_repository import TrainingRepository
from flask import g


class TrainingService:
    def __init__(self):
        self.training_repository = TrainingRepository()

    MONTH_NAMES_ES = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]


    @handle_exceptions
    def get_calendar(self, offset):
        today = date.today()
        year = today.year
        month = today.month + offset

        year += (month - 1) // 12
        month = (month - 1) % 12 + 1

        first_day = date(year, month, 1)
        last_day = date(year, month, calendar.monthrange(year, month)[1])
        first_day_num = first_day.isoweekday()

        calendar_data, calendar_status = self.training_repository.get_calendar(first_day, last_day)
        if calendar_status != 200:
            return calendar_data, calendar_status
        
        training_calendar = []
        for day in range((last_day - first_day).days + 1):
            current_day = first_day + timedelta(days=day)
            day_trainings = calendar_data.get(current_day, [])

            if day_trainings:
                trainings_for_day = [
                    {
                        "technician_name": format_name(t.technician.name, True),
                        "id": t.id,
                        "machine_model": t.machine.model,
                        "machine_image": t.machine.image,
                        "status_id": t.status_id,
                        "training_start": t.training_start.strftime('%H:%M'),
                    }
                    for t in day_trainings
                ]
            else:
                trainings_for_day = []

            training_calendar.append({
                "day": current_day.strftime('%d'),
                "trainings": trainings_for_day
            })

        return {
            "month_name": f"{self.MONTH_NAMES_ES[month - 1]} {year}",
            "calendar": training_calendar,
            "empty_days": first_day_num
        }, 200
    

    @handle_exceptions
    def get_by_id(self, training_id):
        training, tc = self.training_repository.get_training_by_id(training_id)
        if tc != 200:
            return training, tc
  
        result = {
            "technician_name": format_name(training.technician.name, True),
            "client_name": format_name(training.client.name),
            "client_document": training.client.document,
            "client_phone": training.client.phone,
            "id": training.id,
            "machine_model": training.machine.model,
            "machine_image": training.machine.image,
            "status_id": training.status_id,
            "training_start": training.training_start.strftime('%H:%M'),
        }
        return result, 200