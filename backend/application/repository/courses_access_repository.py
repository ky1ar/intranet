import logging
from uuid import uuid4
from flask import g
from application.handlers import handle_db_exceptions
from application.utils import peru_time
from application.db_models.courses_model import (
    CourseAccount, Course, CoursePurchase, CourseCountry,
)


class CoursesAccessRepository:
    """Operaciones contra la BD de la plataforma de cursos (bind 'courses')."""

    @handle_db_exceptions
    def grant_course_access(self, email, first_name, last_name, course_uuid,
                            pin_hash, is_lite=1, default_country_iso="PE"):
        """
        Asegura la cuenta del cliente y le otorga acceso al curso.
        Todo en una sola transacción (un commit) sobre el bind 'courses'.

        - Si no existe cuenta con ese email -> la crea (UUID, status ACTIVE,
          PIN ya hasheado). created_account = True.
        - Si ya existe -> no se toca el PIN. created_account = False.
        - Si la cuenta aún no posee el curso -> inserta la compra (is_lite).

        Devuelve ({...}, 200) o (mensaje, code) ante error de negocio.
        """
        course = (
            g.db_session.query(Course)
            .filter(Course.uuid == course_uuid)
            .first()
        )
        if not course:
            return f"El curso '{course_uuid}' no existe en la plataforma de cursos", 404

        account = (
            g.db_session.query(CourseAccount)
            .filter(CourseAccount.email == email)
            .first()
        )

        created_account = False
        if not account:
            country = (
                g.db_session.query(CourseCountry)
                .filter(CourseCountry.iso == default_country_iso)
                .first()
            )
            account = CourseAccount(
                id=str(uuid4()),
                first_name=first_name or email,
                last_name=last_name or "",
                email=email,
                password=pin_hash,
                status="ACTIVE",
                language="es",
                country_id=country.id if country else None,
                created_at=peru_time(),
                change_pass=1,
            )
            g.db_session.add(account)
            g.db_session.flush()
            created_account = True

        owns = (
            g.db_session.query(CoursePurchase)
            .filter(
                CoursePurchase.client_id == account.id,
                CoursePurchase.course_uuid == course.uuid,
            )
            .first()
        )
        already_owned = owns is not None
        if not already_owned:
            g.db_session.add(CoursePurchase(
                client_id=account.id,
                course_uuid=course.uuid,
                is_lite=is_lite,
                created_at=peru_time(),
            ))

        g.db_session.commit()

        return {
            "created_account": created_account,
            "already_owned": already_owned,
            "client_id": account.id,
            "course_uuid": course.uuid,
            "course_name": course.name,
        }, 200

    @handle_db_exceptions
    def grant_fab_access(self, email, first_name, last_name, pin_hash,
                         default_country_iso="PE"):
        """
        Asegura la cuenta del cliente en la plataforma y habilita el acceso FAB
        (modelos STL). NO otorga ningún curso: solo marca fab_enabled = 1.

        - Si no existe cuenta con ese email -> la crea (UUID, status ACTIVE,
          PIN ya hasheado) con fab_enabled = 1. created_account = True.
        - Si ya existe -> no se toca el PIN; solo se pone fab_enabled = 1.

        Devuelve ({...}, 200) o (mensaje, code) ante error de negocio.
        """
        account = (
            g.db_session.query(CourseAccount)
            .filter(CourseAccount.email == email)
            .first()
        )

        created_account = False
        if not account:
            country = (
                g.db_session.query(CourseCountry)
                .filter(CourseCountry.iso == default_country_iso)
                .first()
            )
            account = CourseAccount(
                id=str(uuid4()),
                first_name=first_name or email,
                last_name=last_name or "",
                email=email,
                password=pin_hash,
                status="ACTIVE",
                language="es",
                country_id=country.id if country else None,
                created_at=peru_time(),
                change_pass=1,
                fab_enabled=1,
            )
            g.db_session.add(account)
            g.db_session.flush()
            created_account = True
            already_enabled = False
        else:
            already_enabled = bool(account.fab_enabled)
            account.fab_enabled = 1

        g.db_session.commit()

        return {
            "created_account": created_account,
            "already_enabled": already_enabled,
            "client_id": account.id,
        }, 200
