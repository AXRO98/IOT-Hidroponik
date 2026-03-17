import os
from pathlib import Path


class Config(object):
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")
    BASE_DIR = Path(__file__).resolve().parent.parent
    
    # folder database
    DB_DIR = BASE_DIR / "database"
    
    # pastikan folder ada
    DB_DIR.mkdir(exist_ok=True)
    
    # file database
    DATABASE = DB_DIR / "database.db"


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