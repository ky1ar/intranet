import logging
import secrets
import string
from application import bcrypt
from application.handlers import handle_exceptions
from application.repository.courses_access_repository import CoursesAccessRepository
from config import Courses


# Mapea el slug del tipo de approval -> UUID del curso en la plataforma de cursos.
# Los UUIDs vienen del entorno porque difieren entre dev y prod
# (COURSES_FDM_UUID / COURSES_LCD_UUID). Se otorga la versión Lite (is_lite=1).
COURSE_UUID_BY_TYPE = {
    "curso-fdm": Courses.FDM_COURSE_UUID,
    "curso-lcd": Courses.LCD_COURSE_UUID,
}

# Slug del tipo de approval para el acceso FAB (biblioteca de modelos STL).
FAB_SLUG = "stl"


def is_course_slug(type_slug):
    """True si el tipo de approval corresponde a un curso aprovisionable."""
    return type_slug in COURSE_UUID_BY_TYPE


def is_fab_slug(type_slug):
    """True si el tipo de approval corresponde al acceso FAB (modelos STL)."""
    return type_slug == FAB_SLUG


def _generate_pin(length=6):
    """Genera un PIN numérico de `length` dígitos (por defecto 6)."""
    return "".join(secrets.choice(string.digits) for _ in range(length))


def _split_name(name):
    parts = (name or "").strip().split()
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


class CoursesProvisioningService:
    def __init__(self):
        self.repository = CoursesAccessRepository()

    @handle_exceptions
    def provision(self, email, name, type_slug):
        """
        Crea/asegura la cuenta en la plataforma de cursos y otorga el curso Lite.
        Solo genera y devuelve `temp_pin` cuando la cuenta es nueva.
        """
        course_uuid = COURSE_UUID_BY_TYPE.get(type_slug)
        if not course_uuid:
            return (
                f"El curso para '{type_slug}' no está configurado en el entorno "
                "(revisa COURSES_FDM_UUID / COURSES_LCD_UUID)",
                400,
            )

        first_name, last_name = _split_name(name)
        temp_pin = _generate_pin()
        pin_hash = bcrypt.generate_password_hash(temp_pin).decode("utf-8")

        result, sc = self.repository.grant_course_access(
            email=email,
            first_name=first_name,
            last_name=last_name,
            course_uuid=course_uuid,
            pin_hash=pin_hash,
            default_country_iso=Courses.DEFAULT_COUNTRY_ISO,
        )
        if sc != 200:
            return result, sc

        result["temp_pin"] = temp_pin if result.get("created_account") else None
        return result, 200


class FabProvisioningService:
    """Acceso FAB (modelos STL) sobre la plataforma de cursos: asegura la cuenta
    y habilita fab_enabled, sin otorgar ningún curso."""

    def __init__(self):
        self.repository = CoursesAccessRepository()

    @handle_exceptions
    def provision(self, email, name):
        """
        Asegura la cuenta en la plataforma y habilita el acceso FAB (fab_enabled = 1).
        No otorga ningún curso. Es idempotente.
        Solo genera y devuelve `temp_pin` cuando la cuenta es nueva.
        """
        first_name, last_name = _split_name(name)
        temp_pin = _generate_pin()
        pin_hash = bcrypt.generate_password_hash(temp_pin).decode("utf-8")

        result, sc = self.repository.grant_fab_access(
            email=email,
            first_name=first_name,
            last_name=last_name,
            pin_hash=pin_hash,
            default_country_iso=Courses.DEFAULT_COUNTRY_ISO,
        )
        if sc != 200:
            return result, sc

        result["temp_pin"] = temp_pin if result.get("created_account") else None
        return result, 200
