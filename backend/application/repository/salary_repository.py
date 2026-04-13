import logging
from datetime import datetime
from application.handlers import handle_db_exceptions
from application.utils import peru_time
from application.db_models.salary_model import AttendancePeriodStats, SalaryConfig, SalaryPeriod, UserBankAccount, BusinessBankConfig
from application.db_models.attendance_model import AttendancePeriod
from flask import g
from sqlalchemy import or_


class SalaryRepository:


    @handle_db_exceptions
    def get_bank_account(self, user_id, business_id):
        account = (
            g.db_session.query(UserBankAccount)
            .filter(
                UserBankAccount.user_id == user_id,
                UserBankAccount.business_id == business_id,
                UserBankAccount.is_active == True,
            )
            .first()
        )
        return account, 200


    @handle_db_exceptions
    def get_business_bank_config(self, business_id):
        config = (
            g.db_session.query(BusinessBankConfig)
            .filter(BusinessBankConfig.business_id == business_id)
            .first()
        )
        return config, 200


    @handle_db_exceptions
    def get_approved_salaries_by_period_and_business(self, period_id, business_id):
        salaries = (
            g.db_session.query(SalaryPeriod)
            .filter(
                SalaryPeriod.period_id == period_id,
                SalaryPeriod.business_id == business_id,
                SalaryPeriod.status == "approved",
            )
            .all()
        )
        return salaries or [], 200

    # ── Stats ──────────────────────────────────────────────────────────

    @handle_db_exceptions
    def upsert_period_stats(self, data):
        existing = (
            g.db_session.query(AttendancePeriodStats)
            .filter(
                AttendancePeriodStats.user_id == data["user_id"],
                AttendancePeriodStats.period_id == data["period_id"],
            )
            .first()
        )

        if existing:
            for key in [
                "target_min", "worked_min", "tolerance_planned_min",
                "tolerance_accum_min", "base_excess_min", "calc_excess_min",
                "calc_obj_min", "tardiness_count", "vacation_days",
                "incomplete_days", "compliance_pct",
            ]:
                setattr(existing, key, data.get(key, 0))
            existing.calculated_at = data["calculated_at"]
            existing.calculated_by = data.get("calculated_by")
            g.db_session.commit()
            return existing, 200

        stats = AttendancePeriodStats(**data)
        g.db_session.add(stats)
        g.db_session.commit()
        return stats, 200


    @handle_db_exceptions
    def get_period_stats(self, user_id, period_id):
        stats = (
            g.db_session.query(AttendancePeriodStats)
            .filter(
                AttendancePeriodStats.user_id == user_id,
                AttendancePeriodStats.period_id == period_id,
            )
            .first()
        )
        return stats, 200


    @handle_db_exceptions
    def get_all_stats_by_period(self, period_id):
        stats = (
            g.db_session.query(AttendancePeriodStats)
            .filter(AttendancePeriodStats.period_id == period_id)
            .all()
        )
        return stats or [], 200


    # ── Salary Config ──────────────────────────────────────────────────

    @handle_db_exceptions
    def get_salary_config(self, user_id, period_end_date):
        config = (
            g.db_session.query(SalaryConfig)
            .filter(
                SalaryConfig.user_id == user_id,
                SalaryConfig.effective_from <= period_end_date,
                or_(
                    SalaryConfig.effective_to.is_(None),
                    SalaryConfig.effective_to >= period_end_date,
                )
            )
            .order_by(SalaryConfig.effective_from.desc())
            .first()
        )
        return config, 200


    @handle_db_exceptions
    def get_salary_config_by_user(self, user_id):
        config = (
            g.db_session.query(SalaryConfig)
            .filter(SalaryConfig.user_id == user_id)
            .order_by(SalaryConfig.effective_from.desc())
            .first()
        )
        return config, 200


    @handle_db_exceptions
    def upsert_salary_config(self, data):
        user_id = data["user_id"]

        # Cerrar config anterior si existe
        current = (
            g.db_session.query(SalaryConfig)
            .filter(
                SalaryConfig.user_id == user_id,
                SalaryConfig.effective_to.is_(None),
            )
            .first()
        )

        effective_from = data["effective_from"]

        if current:
            current.effective_to = effective_from

        config = SalaryConfig(
            user_id=user_id,
            business_id=data["business_id"],
            base_salary=data["base_salary"],
            currency=data.get("currency", "PEN"),
            effective_from=effective_from,
        )
        g.db_session.add(config)
        g.db_session.commit()
        return config, 200


    # ── Salary Period ──────────────────────────────────────────────────

    @handle_db_exceptions
    def upsert_salary_period(self, data):
        existing = (
            g.db_session.query(SalaryPeriod)
            .filter(
                SalaryPeriod.user_id == data["user_id"],
                SalaryPeriod.period_id == data["period_id"],
            )
            .first()
        )

        if existing:
            existing.stats_id = data["stats_id"]
            existing.business_id = data["business_id"]
            existing.base_salary = data["base_salary"]
            existing.compliance_pct = data["compliance_pct"]
            existing.factor = data["factor"]
            existing.final_salary = data["final_salary"]
            existing.status = "draft"
            existing.approved_by = None
            existing.approved_at = None
        else:
            salary = SalaryPeriod(**data)
            g.db_session.add(salary)

        g.db_session.commit()
        return "OK", 200


    @handle_db_exceptions
    def get_salary_period(self, user_id, period_id):
        salary = (
            g.db_session.query(SalaryPeriod)
            .filter(
                SalaryPeriod.user_id == user_id,
                SalaryPeriod.period_id == period_id,
            )
            .first()
        )
        return salary, 200


    @handle_db_exceptions
    def get_salaries_by_period(self, period_id):
        salaries = (
            g.db_session.query(SalaryPeriod)
            .filter(SalaryPeriod.period_id == period_id)
            .all()
        )
        return salaries or [], 200


    @handle_db_exceptions
    def approve_salary(self, salary_id, approved_by):
        salary = g.db_session.query(SalaryPeriod).get(salary_id)
        if not salary:
            return "No encontrado", 404

        salary.status = "approved"
        salary.approved_by = approved_by
        salary.approved_at = peru_time()
        g.db_session.commit()
        return "Aprobado", 200


    @handle_db_exceptions
    def get_period_by_id(self, period_id):
        period = g.db_session.query(AttendancePeriod).get(period_id)
        if not period:
            return None, 404
        return period, 200