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
    
    # ================================================
    # WEBSOCKET CONFIGURATION
    # ================================================
    SOCKETIO_CORS_ALLOWED = os.getenv("SOCKETIO_CORS_ALLOWED", "*")
    SOCKETIO_PING_TIMEOUT = int(os.getenv("SOCKETIO_PING_TIMEOUT", 60))
    SOCKETIO_PING_INTERVAL = int(os.getenv("SOCKETIO_PING_INTERVAL", 25))
    
    # ================================================
    # SIMULATION MODE (untuk development tanpa MQTT broker)
    # ================================================
    ENABLE_SIMULATION = os.getenv("ENABLE_SIMULATION", "True") == "True"
    SIMULATION_INTERVAL = int(os.getenv("SIMULATION_INTERVAL", 1))  # detik per sensor


class Debug(Config):
    DEBUG = True
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    
    # Development specific MQTT (bisa pakai broker lokal atau test)
    MQTT_BROKER = os.getenv("DEV_MQTT_BROKER", "localhost")
    MQTT_PORT = int(os.getenv("DEV_MQTT_PORT", 1883))
    MQTT_USERNAME = os.getenv("DEV_MQTT_USERNAME", "")
    MQTT_PASSWORD = os.getenv("DEV_MQTT_PASSWORD", "")
    
    # Di development, kita bisa matikan auto-connect jika tidak ada broker
    MQTT_AUTO_CONNECT = os.getenv("DEV_MQTT_AUTO_CONNECT", "False") == "True"
    
    # Aktifkan simulasi di development jika MQTT tidak terhubung
    ENABLE_SIMULATION = os.getenv("DEV_ENABLE_SIMULATION", "True") == "True"
    
    # Development WebSocket (allow all origins for testing)
    SOCKETIO_CORS_ALLOWED = os.getenv("DEV_SOCKETIO_CORS_ALLOWED", "*")
    
    # Logging level untuk development
    LOG_LEVEL = "DEBUG"


class Production(Config):
    DEBUG = False
    SECRET_KEY = os.getenv("SECRET_KEY", "production-secret-key")
    
    # Production MQTT (biasanya broker eksternal)
    MQTT_BROKER = os.getenv("PROD_MQTT_BROKER", "mqtt.example.com")
    MQTT_PORT = int(os.getenv("PROD_MQTT_PORT", 1883))
    MQTT_USERNAME = os.getenv("PROD_MQTT_USERNAME", "")
    MQTT_PASSWORD = os.getenv("PROD_MQTT_PASSWORD", "")
    MQTT_AUTO_CONNECT = os.getenv("PROD_MQTT_AUTO_CONNECT", "True") == "True"
    
    # Di production, matikan simulasi
    ENABLE_SIMULATION = False
    
    # Production WebSocket (hanya allow specific domains)
    SOCKETIO_CORS_ALLOWED = os.getenv("PROD_SOCKETIO_CORS_ALLOWED", "https://yourdomain.com")
    
    # Logging level untuk production
    LOG_LEVEL = "WARNING"


class Testing(Config):
    """Testing configuration (opsional)"""
    TESTING = True
    DEBUG = True
    
    # Use in-memory database for testing
    DATABASE = ":memory:"
    
    # Disable MQTT for testing
    MQTT_AUTO_CONNECT = False
    ENABLE_SIMULATION = False
    
    # Test WebSocket
    SOCKETIO_CORS_ALLOWED = "*"


config_dict = {
    "Debug": Debug,
    "Production": Production,
    "Testing": Testing,
    "Development": Debug,  # Alias untuk Debug
    "Prod": Production      # Alias untuk Production
}