"""
Module      : apps.services.mqtt_service
Author      : Keyfin Suratman
Description : Service untuk mengelola data sensor dari MQTT
Created     : 2026-03-23
Updated     : 2026-03-26
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional

# Perbaiki import model
from apps.services.models import SensorDataModel
from apps.utils import log_mqtt, log_info, log_success, log_warning, log_error

# Dictionary untuk menyimpan data sensor terbaru (in-memory cache)
sensor_data_cache = {
    'temperature': None,
    'humidity': None,
    'pressure': None,
    'ph': None,
    'tds': None,
    'water_level': None,
    'last_update': None,
    'all_sensors': {}
}


def process_sensor_data(payload: Dict[str, Any]) -> None:
    """
    Proses data sensor dari MQTT dan kirim sekaligus (bulk) ke WebSocket.
    """
    try:
        from apps.services.websocket_service import websocket_service

        # ================================
        # TIMESTAMP
        # ================================
        timestamp = payload.pop('timestamp', None) or datetime.now().isoformat()

        # ================================
        # KUMPULKAN SEMUA SENSOR
        # ================================
        all_sensor_data = {}

        for sensor_name, sensor_value in payload.items():

            # Skip metadata
            if sensor_name.startswith('_'):
                continue

            if sensor_value is None:
                continue

            all_sensor_data[sensor_name] = {
                'value': float(sensor_value),
                'unit': None,
                'timestamp': timestamp
            }

        # ================================
        # KIRIM SEKALIGUS (BULK)
        # ================================
        if all_sensor_data:
            websocket_service.on_mqtt_message_received(
                topic="sensor/all",
                payload=all_sensor_data
            )

    except Exception as e:
        error_msg = str(e)
        log_error(f"Error processing sensor data: {error_msg}")
        log_mqtt("ERROR", "process_sensor_data", error_msg)

def extract_sensor_type(topic: str) -> str:
    """
    Extract sensor type from MQTT topic.
    
    Mencocokkan topic dengan keyword yang dikenal untuk menentukan tipe sensor.
    
    Args:
        topic (str): MQTT topic string (contoh: "sensors/temperature/data")
        
    Returns:
        str: Sensor type ('temperature', 'humidity', 'pressure', 'ph', 'tds', 
             'water_level', atau 'unknown')
             
    Contoh:
        >>> extract_sensor_type("sensors/temperature/data")
        'temperature'
        >>> extract_sensor_type("devices/sensor_01/ph")
        'ph'
        >>> extract_sensor_type("unknown/topic")
        'unknown'
    """
    if 'temperature' in topic:
        return 'temperature'
    elif 'humidity' in topic:
        return 'humidity'
    elif 'pressure' in topic:
        return 'pressure'
    elif 'ph' in topic or 'pH' in topic:
        return 'ph'
    elif 'tds' in topic or 'ppm' in topic:
        return 'tds'
    elif 'water' in topic or 'level' in topic:
        return 'water_level'
    else:
        # Try to extract from topic parts
        parts = topic.split('/')
        if len(parts) >= 2:
            return parts[-1]  # Last part as sensor type
        return 'unknown'


def get_default_unit(sensor_type: str) -> str:
    """
    Get default unit for sensor type.
    
    Mengembalikan unit pengukuran default berdasarkan tipe sensor.
    
    Args:
        sensor_type (str): Tipe sensor ('temperature', 'humidity', dll)
        
    Returns:
        str: Unit pengukuran (contoh: '°C', '%', 'hPa', 'pH', 'ppm', 'cm')
        
    Contoh:
        >>> get_default_unit("temperature")
        '°C'
        >>> get_default_unit("unknown")
        ''
    """
    units = {
        'temperature': '°C',
        'humidity': '%',
        'pressure': 'hPa',
        'ph': 'pH',
        'tds': 'ppm',
        'water_level': 'cm',
        'unknown': ''
    }
    return units.get(sensor_type, '')


def get_latest_sensor_data() -> Dict[str, Any]:
    """
    Get latest sensor data from cache.
    
    Mengambil data sensor terbaru yang tersimpan di cache.
    Berguna untuk menampilkan data real-time di dashboard.
    
    Args:
        None
        
    Returns:
        dict: Data sensor terkini dengan struktur:
            {
                'temperature': {'value': 25.5, 'unit': '°C', 'timestamp': '...', 'raw_data': {...}},
                'humidity': {...},
                'pressure': {...},
                'ph': {...},
                'tds': {...},
                'water_level': {...},
                'last_update': datetime,
                'status': 'active' or 'no_data'
            }
            
    Contoh:
        >>> latest = get_latest_sensor_data()
        >>> print(latest['temperature']['value'])
        25.5
        >>> print(latest['status'])
        'active'
    """
    return {
        'temperature': sensor_data_cache.get('temperature'),
        'humidity': sensor_data_cache.get('humidity'),
        'pressure': sensor_data_cache.get('pressure'),
        'ph': sensor_data_cache.get('ph'),
        'tds': sensor_data_cache.get('tds'),
        'water_level': sensor_data_cache.get('water_level'),
        'last_update': sensor_data_cache.get('last_update'),
        'status': 'active' if sensor_data_cache['last_update'] else 'no_data'
    }


def get_sensor_history(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get sensor history from cache.
    
    Mengambil riwayat data sensor dengan jumlah maksimum yang ditentukan.
    Data diurutkan dari yang terbaru ke terlama.
    
    Args:
        limit (int, optional): Jumlah maksimum record yang diambil. Default: 50
        
    Returns:
        list: Daftar data sensor dengan format:
            [
                {
                    'timestamp': '2024-03-26T10:30:00.123456',
                    'topic': 'sensors/temperature/data',
                    'data': {...},
                    'sensor_type': 'temperature'
                },
                ...
            ]
            
    Contoh:
        >>> history = get_sensor_history(10)
        >>> for record in history:
        ...     print(f"{record['timestamp']}: {record['sensor_type']} = {record['data']}")
    """
    history = []
    for timestamp, data in sorted(sensor_data_cache['all_sensors'].items(), reverse=True)[:limit]:
        history.append({
            'timestamp': timestamp,
            **data
        })
    return history


def publish_command(topic: str, command: str, value: Any = None) -> bool:
    """
    Publish command to MQTT broker.
    
    Mengirim perintah kontrol ke perangkat melalui MQTT.
    Berguna untuk mengontrol actuator atau mengirim command ke sensor.
    
    Args:
        topic (str): Target topic (contoh: "actuators/light/command")
        command (str): Command name (contoh: "set_state", "calibrate")
        value (any, optional): Command value (contoh: "ON", 25.5, {"mode": "auto"})
        
    Returns:
        bool: True jika publish berhasil, False jika gagal
        
    Contoh:
        >>> # Nyalakan lampu
        >>> publish_command("actuators/light/command", "set_state", "ON")
        True
        
        >>> # Set suhu target heater
        >>> publish_command("actuators/heater/command", "set_temperature", 25.5)
        True
        
        >>> # Kalibrasi sensor pH
        >>> publish_command("sensors/ph/command", "calibrate", {"point": 7.0})
        True
    """
    from apps.services.mqtt_client import mqtt_client
    
    payload = {
        'command': command,
        'value': value,
        'timestamp': datetime.now().isoformat()
    }
    
    log_mqtt("SEND", topic, f"Command: {command}={value}")
    
    success = mqtt_client.publish(topic, payload)
    
    if success:
        log_success(f"Command published: {command}={value} to topic {topic}")
        log_mqtt("PUB-ACK", topic, f"Command sent successfully")
    else:
        log_error(f"Failed to publish command to topic {topic}")
        log_mqtt("ERROR", topic, f"Failed to send command: {command}")
    
    return success


def clear_sensor_cache() -> None:
    """
    Clear sensor data cache.
    
    Menghapus semua data sensor yang tersimpan di cache.
    Berguna untuk reset data atau debugging.
    
    Args:
        None
        
    Returns:
        None
        
    Contoh:
        >>> clear_sensor_cache()
        # Semua data cache di-reset ke None
        # Log: "Sensor cache cleared"
    """
    sensor_data_cache['temperature'] = None
    sensor_data_cache['humidity'] = None
    sensor_data_cache['pressure'] = None
    sensor_data_cache['ph'] = None
    sensor_data_cache['tds'] = None
    sensor_data_cache['water_level'] = None
    sensor_data_cache['last_update'] = None
    sensor_data_cache['all_sensors'] = {}
    log_info("Sensor cache cleared")
    log_mqtt("CLEAR", "cache", "Sensor cache cleared")