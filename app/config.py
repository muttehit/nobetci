"""loads config files from environment and env file"""

from enum import Enum

from decouple import config
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = config(
    "SQLALCHEMY_DATABASE_URL", default="sqlite:///nobetci.sqlite3"
)
SQLALCHEMY_CONNECTION_POOL_SIZE = config(
    "SQLALCHEMY_CONNECTION_POOL_SIZE", default=10, cast=int
)
SQLALCHEMY_CONNECTION_MAX_OVERFLOW = config(
    "SQLALCHEMY_CONNECTION_MAX_OVERFLOW", default=-1, cast=int
)

SERVICE_ADDRESS = config("SERVICE_ADDRESS", default="0.0.0.0")
SERVICE_PORT = config("SERVICE_PORT", cast=int, default=53042)
INSECURE = config("INSECURE", cast=bool, default=False)

DEFAULT_LIMIT = config("DEFAULT_LIMIT", cast=int, default=1)

PANEL_USERNAME = config("PANEL_USERNAME", default="")
PANEL_PASSWORD = config("PANEL_PASSWORD", default="")
PANEL_ADDRESS = config("PANEL_ADDRESS", default="")

SSL_CERT_FILE = config("SSL_CERT_FILE", default="./ssl_cert.pem")
SSL_KEY_FILE = config("SSL_KEY_FILE", default="./ssl_key.pem")
SSL_CLIENT_CERT_FILE = config("SSL_CLIENT_CERT_FILE", default="")

BAN_INTERVAL = config("BAN_INTERVAL", cast=int, default=10)
STL = config("STL", cast=int, default=10)
IUL = config("IUL", cast=int, default=50)
BAN_LAST_USER = config("BAN_LAST_USER", cast=bool, default=False)

API_USERNAME = config("API_USERNAME")
API_PASSWORD = config("API_PASSWORD")

SECRET_KEY = config("SECRET_KEY", default="")
ALGORITHM = config("ALGORITHM", default="HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = config(
    "ACCESS_TOKEN_EXPIRE_MINUTES", cast=int, default=1440)

TELEGRAM_API_TOKEN = config("TELEGRAM_API_TOKEN", default="")
TELEGRAM_ADMIN_ID = config("TELEGRAM_ADMIN_ID", default="",
                           cast=lambda v: [
                               int(i) for i in filter(str.isdigit, (s.strip() for s in v.split(",")))
                           ],)
TELEGRAM_LOGGER_CHANNEL_ID = config(
    "TELEGRAM_LOGGER_CHANNEL_ID", cast=int, default=0)


UVICORN_HOST = config("UVICORN_HOST", default="0.0.0.0")
UVICORN_PORT = config("UVICORN_PORT", cast=int, default=8307)
UVICORN_UDS = config("UVICORN_UDS", default=None)
UVICORN_SSL_CERTFILE = config("UVICORN_SSL_CERTFILE", default=None)
UVICORN_SSL_KEYFILE = config("UVICORN_SSL_KEYFILE", default=None)

DEBUG = config("DEBUG", cast=bool, default=False)
DOCS = config("DOCS", cast=bool, default=False)


class AuthAlgorithm(Enum):
    PLAIN = "plain"
    XXH128 = "xxh128"


AUTH_GENERATION_ALGORITHM = config(
    "AUTH_GENERATION_ALGORITHM", cast=AuthAlgorithm, default=AuthAlgorithm.XXH128
)
