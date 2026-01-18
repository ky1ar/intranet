import logging
from collections import defaultdict
from datetime import datetime, time, date, timedelta
from calendar import monthrange
from application.handlers import handle_db_exceptions
from application.utils import peru_time
from application.db_models.attendance_model import AttendanceMark, AttendancePeriod, UserWorkProfile, WorkProfileShift, AttendanceDayAdjustment
from application.db_models.leave_model import LeaveDuration, LeaveType, LeaveRequest
from application.models import Holidays
from flask import g


class AttendanceRepository:

    @handle_db_exceptions
    def get_adjustments_by_range(self, start_date, end_date):
        rows = (
            g.db_session.query(AttendanceDayAdjustment)
            .filter(AttendanceDayAdjustment.is_active.is_(True))
            .filter(AttendanceDayAdjustment.date >= start_date)
            .filter(AttendanceDayAdjustment.date <= end_date)
            .order_by(AttendanceDayAdjustment.date.asc(), AttendanceDayAdjustment.id.asc())
            .all()
        )
        return rows or [], 200


    @handle_db_exceptions
    def get_user_profile_start_in_period(self, user_id: int, period_start: date, period_end: date):
        row = (
            g.db_session.query(UserWorkProfile)
            .filter(UserWorkProfile.user_id == int(user_id))
            # el perfil se cruza con el periodo
            .filter(UserWorkProfile.start_date <= period_end)
            .filter((UserWorkProfile.end_date.is_(None)) | (UserWorkProfile.end_date >= period_start))
            .order_by(UserWorkProfile.start_date.asc())
            .first()
        )
        if not row:
            return None, 200
        return row.start_date, 200

    
    @handle_db_exceptions
    def get_user_work_profile_row_in_range(self, user_id: int, start_date: date, end_date: date):
        row = (
            g.db_session.query(UserWorkProfile)
            .filter(UserWorkProfile.user_id == int(user_id))
            # cruza con el periodo
            .filter(UserWorkProfile.start_date <= end_date)
            .filter((UserWorkProfile.end_date.is_(None)) | (UserWorkProfile.end_date >= start_date))
            .order_by(UserWorkProfile.start_date.asc())
            .first()
        )
        return row, 200


    @handle_db_exceptions
    def get_durations(self):
        durations = g.db_session.query(LeaveDuration).order_by(LeaveDuration.name).all()
        if not durations:
            return [], 400
        
        return durations, 200
    

    @handle_db_exceptions
    def get_leaves(self):
        leaves = g.db_session.query(LeaveType).order_by(LeaveType.name).all()
        if not leaves:
            return [], 400
        
        return leaves, 200


    @handle_db_exceptions
    def get_existing_keys(self, user_ids, dates):
        if not user_ids or not dates:
            return set(), 200

        rows = (
            g.db_session.query(AttendanceMark.user_id, AttendanceMark.date, AttendanceMark.mark_at)
            .filter(AttendanceMark.user_id.in_(list(user_ids)))
            .filter(AttendanceMark.date.in_(list(dates)))
            .all()
        )

        existing = set()
        for uid, d, t in rows:
            existing.add((int(uid), d.isoformat(), t.strftime("%H:%M")))
        return existing, 200
    

    @handle_db_exceptions
    def bulk_insert_marks(self, marks_rows):
        if not marks_rows:
            return {"inserted": 0}, 200

        objs = [
            AttendanceMark(
                user_id=r["user_id"],
                date=r["date"],
                mark_at=r["mark_at"],
            )
            for r in marks_rows
        ]

        g.db_session.bulk_save_objects(objs)
        g.db_session.commit()
        return {"inserted": len(objs)}, 200


    @handle_db_exceptions
    def existing_marks_set(self, user_id, dates):
        if not dates:
            return set(), 200

        rows = (
            g.db_session.query(AttendanceMark.date, AttendanceMark.mark_at)
            .filter(AttendanceMark.user_id == user_id)
            .filter(AttendanceMark.date.in_(list(dates)))
            .all()
        )

        existing = set()
        for d, t in rows:
            existing.add((d.isoformat(), t.strftime("%H:%M")))
        return existing, 200


    @handle_db_exceptions
    def save_marks(self, marks_rows):
        if not marks_rows:
            return {"inserted": 0, "skipped_duplicates": 0}, 200

        user_ids = {r["user_id"] for r in marks_rows}
        dates = {r["date"] for r in marks_rows}

        existing = (
            g.db_session.query(AttendanceMark.user_id, AttendanceMark.date, AttendanceMark.mark_at)
            .filter(AttendanceMark.user_id.in_(list(user_ids)))
            .filter(AttendanceMark.date.in_(list(dates)))
            .all()
        )

        existing_set = {
            (int(uid), d.isoformat(), t.strftime("%H:%M"))
            for uid, d, t in existing
        }

        seen = set()
        to_insert = []
        skipped = 0

        for r in marks_rows:
            key = (int(r["user_id"]), r["date"].isoformat(), r["mark_at"].strftime("%H:%M"))

            if key in existing_set or key in seen:
                skipped += 1
                continue

            seen.add(key)
            to_insert.append(
                AttendanceMark(
                    user_id=int(r["user_id"]),
                    date=r["date"],
                    mark_at=r["mark_at"],
                    created_at=peru_time(),
                )
            )

        if to_insert:
            g.db_session.bulk_save_objects(to_insert)
            g.db_session.commit()

        return {"inserted": len(to_insert), "skipped_duplicates": skipped}, 200
    
        
    def _add_months(self, d, months):
        y = d.year + (d.month - 1 + months) // 12
        m = (d.month - 1 + months) % 12 + 1
        last_day = monthrange(y, m)[1]
        day = min(d.day, last_day)
        return date(y, m, day)


    @handle_db_exceptions
    def get_period_for_month(self, year, month):
        start = date(year, month, 1)
        end = date(year, month, monthrange(year, month)[1])

        p = (
            g.db_session.query(AttendancePeriod)
            .filter(AttendancePeriod.end_date >= start)
            .filter(AttendancePeriod.end_date <= end)
            .order_by(AttendancePeriod.end_date.desc())
            .first()
        )
        return p, 200


    @handle_db_exceptions
    def get_period_by_offset(self, offset, today=None):
        today = today or date.today()
        base_month = date(today.year, today.month, 1)
        target = self._add_months(base_month, int(offset))
        return self.get_period_for_month(target.year, target.month)
    

    @handle_db_exceptions
    def get_marks_by_user_and_range(self, user_id, start_date, end_date):
        rows = (
            g.db_session.query(AttendanceMark)
            .filter(AttendanceMark.user_id == int(user_id))
            .filter(AttendanceMark.date >= start_date)
            .filter(AttendanceMark.date <= end_date)
            .order_by(AttendanceMark.date.asc(), AttendanceMark.mark_at.asc())
            .all()
        )
        return rows, 200
    

    def _pair_times(self, times_hhmm):
        intervals, i = [], 0
        while i < len(times_hhmm):
            start = times_hhmm[i]
            end = times_hhmm[i+1] if i+1 < len(times_hhmm) else None
            intervals.append({"start": start, "end": end})
            i += 2
        return intervals
    

    def _monday_of(self, d: date) -> date:
        return d - timedelta(days=d.weekday())
    

    @handle_db_exceptions
    def build_period_summary(self, user_id: int, period: AttendancePeriod):
        marks, mc = self.get_marks_by_user_and_range(user_id, period.start_date, period.end_date)
        if mc != 200:
            return marks, mc

        holidays_map, hc = self.get_holidays_by_range(period.start_date, period.end_date)
        if hc != 200:
            return holidays_map, hc

        by_date = defaultdict(list)
        for m in marks:
            by_date[m.date].append(m.mark_at.strftime("%H:%M"))

        start = self._monday_of(period.start_date)
        end = period.end_date

        weeks, week_index = [], 1
        d = start
        while d <= end:
            days = []
            for _ in range(7):
                date_iso = d.isoformat()
                times = by_date.get(d, [])

                holiday = holidays_map.get(date_iso)

                days.append({
                    "date": date_iso,
                    "label": d.strftime("%d"),               # keep numeric label for your current UI
                    "intervals": self._pair_times(times),
                    "in_period": (period.start_date <= d <= period.end_date),

                    # ✅ NEW
                    "holiday": holiday,                      # None or {id,name,date,hex_color}
                    "is_holiday": bool(holiday),             # easy for front -> add class
                })
                d += timedelta(days=1)

            weeks.append({"week_index": week_index, "days": days})
            week_index += 1

        return {
            "period": {
                "id": period.id,
                "name": period.name,
                "start_date": period.start_date.isoformat(),
                "end_date": period.end_date.isoformat(),
            },
            "weeks": weeks,
        }, 200
    

    @handle_db_exceptions
    def get_profile_for_user_on_date(self, user_id, on_date):
        row = (
            g.db_session.query(UserWorkProfile)
            .filter(UserWorkProfile.user_id == int(user_id))
            .filter(UserWorkProfile.start_date <= on_date)
            .filter((UserWorkProfile.end_date.is_(None)) | (UserWorkProfile.end_date >= on_date))
            .order_by(UserWorkProfile.start_date.desc())
            .first()
        )
        if not row:
            return None, 200
        return row.profile, 200
    
    
    @handle_db_exceptions
    def get_shifts_for_profile(self, profile_id):
        rows = (
            g.db_session.query(WorkProfileShift)
            .filter(WorkProfileShift.profile_id == int(profile_id))
            .order_by(WorkProfileShift.weekday.asc(), WorkProfileShift.start_time.asc())
            .all()
        )
        return rows or [], 200
    

    @handle_db_exceptions
    def get_holidays_by_range(self, start_date, end_date):
        rows = (
            g.db_session.query(Holidays)
            .filter(Holidays.date >= start_date)
            .filter(Holidays.date <= end_date)
            .filter(Holidays.deleted_at.is_(None))
            .all()
        )

        mp = {}
        for h in (rows or []):
            mp[h.date.isoformat()] = {
                "id": h.id,
                "name": h.name,
                "date": h.date.isoformat(),
                "hex_color": getattr(h, "hex_color", None),
            }

        return mp, 200
    

    @handle_db_exceptions
    def get_marks_by_user_and_date(self, user_id, d):
        rows = (
            g.db_session.query(AttendanceMark)
            .filter(AttendanceMark.user_id == int(user_id))
            .filter(AttendanceMark.date == d)
            .order_by(AttendanceMark.mark_at.asc())
            .all()
        )
        return rows or [], 200
    

    @handle_db_exceptions
    def get_holiday_on_date(self, d):
        row = (
            g.db_session.query(Holidays)
            .filter(Holidays.date == d)
            .filter(Holidays.deleted_at.is_(None))
            .first()
        )
        if not row:
            return None, 200
        return {
            "id": row.id,
            "name": row.name,
            "date": row.date.isoformat(),
            "hex_color": getattr(row, "hex_color", None),
        }, 200
    

    @handle_db_exceptions
    def insert_marks_with_meta(self, marks_rows):
        if not marks_rows:
            return {"inserted": 0}, 200

        to_insert = []
        for r in marks_rows:
            to_insert.append(
                AttendanceMark(
                    user_id=int(r["user_id"]),
                    date=r["date"],
                    mark_at=r["mark_at"],
                    created_at=peru_time(),
                    created_by=int(r["created_by"]),
                )
            )

        g.db_session.bulk_save_objects(to_insert)
        g.db_session.commit()
        return {"inserted": len(to_insert)}, 200


    @handle_db_exceptions
    def insert_leave_request(self, data):
        obj = LeaveRequest(
            user_id=data.get("user_id"),
            request_type='Permiso' if data.get("type") == 'permit' else "Vacaciones",
            status_id=1 if data.get("level_id") == 2 else 2,
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            duration_id=data.get("duration_id"),
            leave_type_id=data.get("leave_type_id"),
            leave_type_detail=data.get("leave_type_detail"),
            motive=data.get("motive"),
            recovery_plan=data.get("recovery_plan"),
            assigned_user_id=data.get("assigned_user_id"),
            description=data.get("description"),
            created_at=peru_time(),
        )
        g.db_session.add(obj)
        g.db_session.commit()
        return {"id": obj.id}, 200


    @handle_db_exceptions
    def get_leave_requests(self, visibility):
        query  = (
            g.db_session.query(LeaveRequest)
            .filter(LeaveRequest.deleted_at.is_(None))
        )
        if visibility:
            query = query.filter(LeaveRequest.user_id.in_(visibility))

        leave_requests = (
            query
            .order_by(LeaveRequest.id.desc())
            .all()
        )

        if not leave_requests:
            return [], 200

        return leave_requests, 200


    @handle_db_exceptions
    def get_leave_by_id(self, leave_id):
        leave = (
            g.db_session.query(LeaveRequest)
            .filter(
                LeaveRequest.id == leave_id,
                LeaveRequest.deleted_at.is_(None),
            )
            .first()
        )
        if not leave:
            return "Solicitud no encontrada", 404

        return leave, 200
    

    @handle_db_exceptions
    def soft_delete(self, leave_id):
        leave = (
            g.db_session.query(LeaveRequest)
            .filter(
                LeaveRequest.id == leave_id,
                LeaveRequest.deleted_at.is_(None),
            )
            .first()
        )
        if not leave:
            return "Solicitud no encontrada", 404

        leave.deleted_at = peru_time()
        g.db_session.commit()
        return "Solicitud eliminada", 200


    @handle_db_exceptions
    def set_status(self, leave_id, status_id):
        leave = (
            g.db_session.query(LeaveRequest)
            .filter(
                LeaveRequest.id == leave_id,
                LeaveRequest.deleted_at.is_(None),
            )
            .first()
        )
        if not leave:
            return "Solicitud no encontrada", 404

        leave.status_id = status_id
        g.db_session.commit()
        return leave.id, 200


    @handle_db_exceptions
    def update_leave(self, data):
        leave_id = data.get("leave_id")
        leave = (
            g.db_session.query(LeaveRequest)
            .filter(
                LeaveRequest.id == leave_id,
                LeaveRequest.deleted_at.is_(None),
            )
            .first()
        )
        if not leave:
            return "Solicitud no encontrada", 404

        leave.start_date = data.get("start_date")
        leave.end_date = data.get("end_date")
        leave.duration_id = data.get("duration_id")
        leave.leave_type_id = data.get("leave_type_id")
        leave.leave_type_detail = data.get("leave_type_detail")
        leave.motive = data.get("motive")
        leave.recovery_plan = data.get("recovery_plan")
        leave.assigned_user_id = data.get("assigned_user_id")
        leave.description = data.get("description")
        
        g.db_session.commit()
        return leave.id, 200