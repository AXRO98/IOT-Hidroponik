"""
File        : __init__.py
Author      : Keyfin Agustio Suratman
Description : Inisialisasi semua services untuk IoT Hidroponik
Created     : 2026-03-20
"""

from datetime import datetime
from apps.utils import log_info, log_success, log_warning

from apps.services.websocket_service import websocket_service, WebSocketService


def init_services(app):
    """
    Inisialisasi semua services dengan Flask app
    
    Args:
        app: Flask application instance
    """
    log_info("Initializing services...")
    
    # Inisialisasi WebSocket Service
    websocket_service.init_app(app)
    
    # Cek apakah perlu menjalankan simulasi
    enable_simulation = app.config.get('ENABLE_SIMULATION', False)
    
    # Jalankan simulasi jika enable simulation = True
    if enable_simulation:
        websocket_service.start_simulation()
        log_info("Simulasi data random via WebSocket dimulai")
    else:
        log_info("Simulasi data dimatikan (ENABLE_SIMULATION=False)")
    
    log_success("All services initialized")
    
    return {
        'websocket': websocket_service
    }


__all__ = [
    'init_services',
    'websocket_service',
    'WebSocketService'
]