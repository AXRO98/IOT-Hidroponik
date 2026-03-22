"""
File        : websocket_service.py
Author      : Keyfin Agustio Suratman
Description : WebSocketIO service untuk real-time communication dengan dashboard
Created     : 2026-03-20
"""

import json
import random
import time
from datetime import datetime
from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect

from apps.utils import log_info, log_success, log_warning, log_error, log_websocket


class WebSocketService:
    """WebSocket Service untuk real-time communication"""
    
    def __init__(self, app=None):
        self.connected_clients = {}
        self.rooms = {}
        self.simulation_running = False  # Flag untuk simulasi
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inisialisasi SocketIO dengan Flask app"""
        
        # Konfigurasi CORS
        cors_allowed = app.config.get('SOCKETIO_CORS_ALLOWED', '*')
        
        # Inisialisasi SocketIO
        self.socketio = SocketIO(
            app,
            cors_allowed_origins=cors_allowed,
            async_mode='threading',
            logger=False,
            engineio_logger=False,
            ping_timeout=60,
            ping_interval=25,
            max_http_buffer_size=10e6  # 10MB
        )
        
        # Register event handlers
        self._register_handlers()
        
        log_success("WebSocketIO Service initialized")
        
        # Simpan service ke app untuk akses global
        app.websocket_service = self
    
    def _register_handlers(self):
        """Register semua event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            client_id = request.sid
            self.connected_clients[client_id] = {
                'connected_at': datetime.now().isoformat(),
                'ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', 'Unknown')
            }
            
            log_websocket("CONNECT", client_id, f"IP: {request.remote_addr}")
            emit('connected', {
                'status': 'connected',
                'client_id': client_id,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            client_id = request.sid
            
            # Leave all rooms
            if client_id in self.rooms:
                for room in self.rooms[client_id]:
                    leave_room(room)
                del self.rooms[client_id]
            
            # Remove from connected clients
            if client_id in self.connected_clients:
                del self.connected_clients[client_id]
            
            log_websocket("DISCONNECT", client_id)
        
        @self.socketio.on('join')
        def handle_join(data):
            """Handle client join room"""
            client_id = request.sid
            room = data.get('room')
            
            if room:
                join_room(room)
                
                # Track rooms
                if client_id not in self.rooms:
                    self.rooms[client_id] = []
                if room not in self.rooms[client_id]:
                    self.rooms[client_id].append(room)
                
                log_websocket("JOIN", client_id, f"Room: {room}")
                
                emit('joined', {
                    'room': room,
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                }, room=client_id)
                
                # Notify others in room
                emit('user_joined', {
                    'user_id': client_id,
                    'room': room,
                    'timestamp': datetime.now().isoformat()
                }, room=room, include_self=False)
        
        @self.socketio.on('leave')
        def handle_leave(data):
            """Handle client leave room"""
            client_id = request.sid
            room = data.get('room')
            
            if room:
                leave_room(room)
                
                # Update room tracking
                if client_id in self.rooms and room in self.rooms[client_id]:
                    self.rooms[client_id].remove(room)
                
                log_websocket("LEAVE", client_id, f"Room: {room}")
                
                emit('left', {
                    'room': room,
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                }, room=client_id)
                
                # Notify others in room
                emit('user_left', {
                    'user_id': client_id,
                    'room': room,
                    'timestamp': datetime.now().isoformat()
                }, room=room, include_self=False)
        
        @self.socketio.on('message')
        def handle_message(data):
            """Handle incoming message from client"""
            client_id = request.sid
            message_type = data.get('type', 'unknown')
            content = data.get('content', {})
            
            log_websocket("MESSAGE", client_id, f"Type: {message_type}")
            
            # Process based on message type
            if message_type == 'sensor_request':
                self._handle_sensor_request(client_id, content)
            elif message_type == 'actuator_command':
                self._handle_actuator_command(client_id, content)
            elif message_type == 'ping':
                emit('pong', {
                    'timestamp': datetime.now().isoformat()
                }, room=client_id)
            else:
                # Default response
                emit('message_received', {
                    'type': message_type,
                    'status': 'received',
                    'timestamp': datetime.now().isoformat()
                }, room=client_id)
        
        @self.socketio.on('error')
        def handle_error(error):
            """Handle socket error"""
            client_id = request.sid
            log_error(f"WebSocket Error - Client: {client_id}, Error: {str(error)}")
    
    def _handle_sensor_request(self, client_id, content):
        """Handle sensor data request"""
        # TODO: Implement sensor data retrieval
        device_id = content.get('device_id')
        sensor_type = content.get('sensor_type')
        
        # Example response
        emit('sensor_data', {
            'device_id': device_id,
            'sensor_type': sensor_type,
            'data': {
                'value': 25.5,
                'unit': '°C',
                'timestamp': datetime.now().isoformat()
            }
        }, room=client_id)
    
    def _handle_actuator_command(self, client_id, content):
        """Handle actuator command"""
        # TODO: Implement actuator control
        device_id = content.get('device_id')
        actuator = content.get('actuator')
        command = content.get('command')
        
        # Example response
        emit('command_ack', {
            'device_id': device_id,
            'actuator': actuator,
            'command': command,
            'status': 'executed',
            'timestamp': datetime.now().isoformat()
        }, room=client_id)
    
    # ========== PUBLIC METHODS ==========
    
    def emit_to_all(self, event, data):
        """Emit event ke semua connected clients"""
        if self.socketio:
            self.socketio.emit(event, data)
            log_websocket("EMIT-ALL", event, str(data)[:100])
    
    def emit_to_room(self, room, event, data):
        """Emit event ke semua clients dalam room"""
        if self.socketio:
            self.socketio.emit(event, data, room=room)
            log_websocket(f"EMIT-ROOM:{room}", event, str(data)[:100])
    
    def emit_to_client(self, client_id, event, data):
        """Emit event ke specific client"""
        if self.socketio:
            self.socketio.emit(event, data, room=client_id)
            log_websocket(f"EMIT-CLIENT:{client_id}", event, str(data)[:100])
    
    def broadcast_sensor_data(self, device_id, sensor_type, value, unit=None):
        """Broadcast sensor data ke semua clients"""
        data = {
            'device_id': device_id,
            'sensor_type': sensor_type,
            'value': value,
            'unit': unit,
            'timestamp': datetime.now().isoformat()
        }
        self.emit_to_all('sensor_update', data)
    
    def broadcast_actuator_status(self, device_id, actuator, status):
        """Broadcast actuator status ke semua clients"""
        data = {
            'device_id': device_id,
            'actuator': actuator,
            'status': status,
            'timestamp': datetime.now().isoformat()
        }
        self.emit_to_all('actuator_update', data)
    
    def send_notification(self, message, notification_type='info', target=None):
        """Send notification ke client(s)"""
        data = {
            'type': notification_type,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        if target:
            if isinstance(target, str):
                # Send ke room atau specific client
                if target.startswith('room:'):
                    room = target[5:]
                    self.emit_to_room(room, 'notification', data)
                else:
                    self.emit_to_client(target, 'notification', data)
            elif isinstance(target, list):
                # Send ke multiple clients
                for client_id in target:
                    self.emit_to_client(client_id, 'notification', data)
        else:
            # Broadcast ke semua
            self.emit_to_all('notification', data)
    
    def get_stats(self):
        """Get WebSocket statistics"""
        return {
            'connected_clients': len(self.connected_clients),
            'clients': self.connected_clients,
            'rooms': self.rooms
        }
    
    # ========== SIMULASI DATA RANDOM ==========

    def _random_data_generator(self):
        """Generator data random yang smooth (tidak loncat jauh)"""

        sensor_types = ['ph', 'tds', 'suhu', 'kelembapan']

        # 🔥 nilai awal (state)
        last_values = {
            'ph': 6.8,
            'tds': 800,
            'suhu': 28.0,
            'kelembapan': 70
        }

        index = 0

        while self.simulation_running:
            sensor_type = sensor_types[index % len(sensor_types)]

            # 🔥 ambil nilai sebelumnya
            prev = last_values[sensor_type]

            # 🔥 perubahan kecil (delta)
            if sensor_type == 'ph':
                delta = random.uniform(-0.2, 0.2)
                value = round(prev + delta, 1)
                value = max(5.5, min(8.0, value))  # batas aman
                unit = ''

            elif sensor_type == 'tds':
                delta = random.randint(-20, 20)
                value = prev + delta
                value = max(500, min(1200, value))
                unit = 'ppm'

            elif sensor_type == 'suhu':
                delta = random.uniform(-0.5, 0.5)
                value = round(prev + delta, 1)
                value = max(18, min(40, value))
                unit = '°C'

            elif sensor_type == 'kelembapan':
                delta = random.randint(-3, 3)
                value = prev + delta
                value = max(40, min(100, value))
                unit = '%'

            # 🔥 simpan nilai baru
            last_values[sensor_type] = value

            yield {
                'device_id': 'simulator',
                'sensor_type': sensor_type,
                'value': value,
                'unit': unit,
                'timestamp': datetime.now().isoformat()
            }

            index += 1
            time.sleep(1)
    
    def start_simulation(self):
        """Mulai simulasi dengan mengirim data random ke semua client"""
        if self.simulation_running:
            log_warning("Simulasi sudah berjalan")
            return
        
        self.simulation_running = True
        log_info("Memulai simulasi data random...")
        
        def task():
            for data in self._random_data_generator():
                if not self.simulation_running:
                    break
                if self.connected_clients:
                    # Broadcast sensor update ke semua client
                    self.socketio.emit('sensor_update', data)
                else:
                    # Jika tidak ada client, tidur sebentar untuk menghemat CPU
                    time.sleep(5)
        
        # Jalankan task di background thread
        self.socketio.start_background_task(task)
    
    def stop_simulation(self):
        """Hentikan simulasi"""
        if not self.simulation_running:
            return
        self.simulation_running = False
        log_info("Simulasi data random dihentikan")


# Singleton instance
websocket_service = WebSocketService()