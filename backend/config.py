import os
from dotenv import load_dotenv, find_dotenv


dotenv_path = find_dotenv()
load_dotenv(dotenv_path, override=True)


class Config:
    VERSION = "1.0"
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 15,
        "max_overflow": 10,
        "pool_timeout": 30,
    }

    API_HOST = os.getenv("API_HOST")
    API_PORT = os.getenv("API_PORT")

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = False #int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES"))
    UPLOAD_FOLDER = os.path.abspath("uploads/")
    UPLOAD_MACHINES_FOLDER = os.path.abspath("uploads/machines/")

    BASE_URL = os.getenv("BASE_URL")
    CONTACT_PHONE = os.getenv("CONTACT_PHONE")
    REVIEW_URL = os.getenv("REVIEW_URL")
    T1_START = os.getenv("T1_START")
    T1_END = os.getenv("T1_END")
    T2_START = os.getenv("T2_START")
    T2_END = os.getenv("T2_END")


class Redis:
    URL = os.getenv("REDIS_URL")


class WABA:
    URL = os.getenv("WABA_URL")
    TOKEN = os.getenv("WABA_TOKEN")
    WEBHOOK_TOKEN = os.getenv("WABA_WEBHOOK_TOKEN")
    SUPPORT_TERMS = os.getenv("SUPPORT_TERMS")


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