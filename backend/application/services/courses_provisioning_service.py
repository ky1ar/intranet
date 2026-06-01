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


def is_course_slug(type_slug):
    """True si el tipo de approval corresponde a un curso aprovisionable."""
    return type_slug in COURSE_UUID_BY_TYPE


def _generate_password(length=10):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


class CoursesProvisioningService:
    def __init__(self):
        self.repository = CoursesAccessRepository()

    @handle_exceptions
    def provision(self, email, name, type_slug):
        """
        Crea/asegura la cuenta en la plataforma de cursos y otorga el curso Lite.
        Solo genera y devuelve `temp_password` cuando la cuenta es nueva.
        """
        course_uuid = COURSE_UUID_BY_TYPE.get(type_slug)
        if not course_uuid:
            return (
                f"El curso para '{type_slug}' no está configurado en el entorno "
                "(revisa COURSES_FDM_UUID / COURSES_LCD_UUID)",
                400,
            )

        first_name, last_name = self._split_name(name)
        temp_password = _generate_password()
        password_hash = bcrypt.generate_password_hash(temp_password).decode("utf-8")

        result, sc = self.repository.grant_course_access(
            email=email,
            first_name=first_name,
            last_name=last_name,
            course_uuid=course_uuid,
            password_hash=password_hash,
            default_country_iso=Courses.DEFAULT_COUNTRY_ISO,
        )
        if sc != 200:
            return result, sc

        result["temp_password"] = temp_password if result.get("created_account") else None
        return result, 200

    @staticmethod
    def _split_name(name):
        parts = (name or "").strip().split()
        if not parts:
            return "", ""
        if len(parts) == 1:
            return parts[0], ""
        return parts[0], " ".join(parts[1:])
