import os
from dotenv import load_dotenv, find_dotenv


dotenv_path = find_dotenv()
load_dotenv(dotenv_path, override=True)


class Config:
    VERSION = "1.0"
    APP_VERSION = "1.8.3"
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
    SQLALCHEMY_BINDS = {
        key: uri
        for key, uri in {"courses": os.getenv("COURSES_DATABASE_URI")}.items()
        if uri
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 15,
        "max_overflow": 10,
        "pool_timeout": 30,
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT"))
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() == "true"
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "false").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_SENDER")


    API_HOST = os.getenv("API_HOST")
    API_PORT = int(os.getenv("API_PORT"))

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = False
    UPLOAD_FOLDER = os.path.abspath("/shared_uploads/")
    UPLOAD_PDF_FOLDER = os.path.abspath("/shared_uploads/pdf/")
    UPLOAD_PICKING_FOLDER = os.path.abspath("/shared_uploads/picking/")
    UPLOAD_MACHINES_FOLDER = os.path.abspath("uploads/machines/")
    UPLOAD_PROPF_FOLDER = os.path.abspath("/shared_uploads/complaint_proof/")
    QR_FOLDER = os.path.abspath("/shared_uploads/qr/")
    

    BASE_URL = os.getenv("BASE_URL")
    CONTACT_PHONE = os.getenv("CONTACT_PHONE")
    SUPPORT_CONTACT_PHONE = os.getenv("SUPPORT_CONTACT_PHONE")
    REVIEW_URL = os.getenv("REVIEW_URL")
    T1_START = os.getenv("T1_START")
    T1_END = os.getenv("T1_END")
    T2_START = os.getenv("T2_START")
    T2_END = os.getenv("T2_END")
    SUPPORT_TERMS = os.getenv("SUPPORT_TERMS")
    EXTERNAL_REGISTER_URL = os.getenv("EXTERNAL_REGISTER_URL")

    COMPLAINT_ATTACHMENTS_MAX_BYTES = 25 * 1024 * 1024
    MAX_CONTENT_LENGTH = 30 * 1024 * 1024


class Courses:
    PLATFORM_URL = os.getenv("COURSES_PLATFORM_URL")
    FAB_URL = os.getenv("COURSES_FAB_URL")
    DEFAULT_COUNTRY_ISO = os.getenv("COURSES_DEFAULT_COUNTRY_ISO", "PE")
    FDM_COURSE_UUID = os.getenv("COURSES_FDM_UUID")
    LCD_COURSE_UUID = os.getenv("COURSES_LCD_UUID")


class Wordpress:
    BASE_URL = os.getenv("WP_BASE_URL")
    WEBHOOK_SECRET = os.getenv("WP_WEBHOOK_SECRET")


class Redis:
    URL = os.getenv("REDIS_URL")


class WABA:
    URL = os.getenv("WABA_URL")
    TOKEN = os.getenv("WABA_TOKEN")
    WEBHOOK_TOKEN = os.getenv("WABA_WEBHOOK_TOKEN")


class Odoo:
    URL = os.getenv("ODOO_URL")
    USER = os.getenv("ODOO_USER")
    API_KEY = os.getenv("ODOO_API_KEY")
    DB = os.getenv("ODOO_DB")
    PDF_URL = os.getenv("PDF_URL")


class ApisNet:
    TOKEN = os.getenv("APISNET_TOKEN")
    URL = os.getenv("APISNET_URL")


class ApiPeru:
    TOKEN = os.getenv("APIPERU_TOKEN")
    URL = os.getenv("APIPERU_URL")


class Shalom:
    TRACK_URL = os.getenv("SHALOM_TRACK_URL")
    STATE_URL = os.getenv("SHALOM_STATE_URL")


class Olva:
    TRACK_URL = os.getenv("OLVA_TRACK_URL")
    API_KEY = os.getenv("OLVA_API_KEY")


class Marvisur:
    TRACK_URL = os.getenv("MARVISUR_TRACK_URL")


class Paths:
    MAX_BYTES = 25 * 1024 * 1024
    IMPORTS = os.path.abspath("/shared_uploads/imports/")
    SAFEBUY = os.path.abspath("/shared_uploads/safebuy/")
    LEAVES = os.path.abspath("/shared_uploads/leaves/")
    REFUND = os.path.abspath("/shared_uploads/refund/")
    APPROVAL_VOUCHERS = os.path.abspath("/shared_uploads/approvals/vouchers/")
    GUIDES_MEDIA = os.path.abspath("/shared_uploads/guides/media/")
    MACHINES = os.path.abspath("/shared_uploads/machines/")
    WHATSAPP = os.path.abspath("/shared_uploads/whatsapp/")