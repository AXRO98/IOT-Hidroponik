import os
from pathlib import Path


class Config(object):
    BASE_DIR = Path(__file__).resolve().parent
    DB_DIR = BASE_DIR / "database"


class Debug(Config):
    DEBUG = True
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")


class Production(Config):
    DEBUG = False
    SECRET_KEY = os.getenv("SECRET_KEY", "production-secret-key")


config_dict = {
    "Debug": Debug,
    "Production": Production
}