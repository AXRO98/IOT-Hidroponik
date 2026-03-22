# Tambahkan di bagian imports
from datetime import datetime

# Tambahkan fungsi-fungsi ini di dalam file utils.py

def log_mqtt(direction, topic, message=""):
    """Log MQTT messages with custom formatting"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    colors = {
        'SEND': '\033[94m',      # Blue
        'RECV': '\033[92m',      # Green
        'PUB-ACK': '\033[93m',   # Yellow
        'ERROR': '\033[91m',     # Red
        'RESET': '\033[0m'
    }
    
    color = colors.get(direction, '\033[0m')
    direction_str = f"[MQTT-{direction}]"
    
    # Truncate long messages
    if len(message) > 200:
        message = message[:200] + "..."
    
    print(f"{color}{direction_str:<15} {topic:<30} {message}{colors['RESET']}")


def log_websocket(action, client_id, details=""):
    """Log WebSocket events with custom formatting"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    colors = {
        'CONNECT': '\033[92m',    # Green
        'DISCONNECT': '\033[91m', # Red
        'JOIN': '\033[94m',       # Blue
        'LEAVE': '\033[93m',      # Yellow
        'MESSAGE': '\033[95m',    # Magenta
        'EMIT-ALL': '\033[96m',   # Cyan
        'EMIT-ROOM': '\033[96m',  # Cyan
        'EMIT-CLIENT': '\033[96m', # Cyan
        'RESET': '\033[0m'
    }
    
    color = colors.get(action, '\033[0m')
    action_str = f"[WS-{action}]"
    
    client_short = client_id[:8] + "..." if len(client_id) > 8 else client_id
    print(f"{color}{action_str:<15} {client_short:<15} {details}{colors['RESET']}")