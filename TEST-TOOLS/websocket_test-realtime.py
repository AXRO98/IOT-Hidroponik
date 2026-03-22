#!/usr/bin/env python3
"""
File        : websocket_monitor.py
Author      : Keyfin Agustio Suratman
Description : WebSocket Monitor untuk monitoring data sensor real-time dengan Socket.IO support
Created     : 2026-03-23
"""

import sys
import json
import time
import argparse
import urllib.parse
from datetime import datetime
from collections import deque

try:
    import websocket
    from colorama import init, Fore, Style
    init()
except ImportError:
    print("Please install required packages:")
    print("pip install websocket-client colorama")
    sys.exit(1)


class WebSocketMonitor:
    """Monitor WebSocket data for IoT Hidroponik dengan Socket.IO support"""
    
    def __init__(self, url: str, socketio_mode: bool = True):
        """
        Initialize WebSocket Monitor
        
        Args:
            url: Base URL (ws://host:port)
            socketio_mode: Use Socket.IO protocol
        """
        self.base_url = url
        self.socketio_mode = socketio_mode
        
        # Build WebSocket URL for Socket.IO if needed
        if self.socketio_mode:
            parsed = urllib.parse.urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            self.url = f"{base_url}/socket.io/?EIO=4&transport=websocket"
        else:
            self.url = url
        
        self.ws = None
        self.running = True
        self.connected = False
        
        # Data storage
        self.sensor_data = {
            'ph': {'value': None, 'timestamp': None},
            'tds': {'value': None, 'timestamp': None},
            'suhu': {'value': None, 'timestamp': None},
            'kelembapan': {'value': None, 'timestamp': None}
        }
        
        # History for graphs (max 60 points)
        self.history = {
            'ph': deque(maxlen=60),
            'tds': deque(maxlen=60),
            'suhu': deque(maxlen=60),
            'kelembapan': deque(maxlen=60)
        }
        
        # Statistics
        self.stats = {
            'messages_received': 0,
            'sensor_updates': 0,
            'connection_time': None
        }
    
    def _parse_socketio_message(self, message):
        """
        Parse Socket.IO protocol message
        
        Socket.IO packet types:
        0 = CONNECT, 1 = DISCONNECT, 2 = EVENT, 3 = ACK, 
        4 = ERROR, 5 = BINARY_EVENT, 6 = BINARY_ACK
        """
        if not message:
            return None, None
        
        try:
            packet_type = int(message[0])
            data = message[1:] if len(message) > 1 else None
            
            if packet_type == 0:  # CONNECT
                return 'connect', data
            elif packet_type == 1:  # DISCONNECT
                return 'disconnect', data
            elif packet_type == 2:  # EVENT
                if data:
                    event_data = json.loads(data)
                    if isinstance(event_data, list) and len(event_data) >= 2:
                        event_name = event_data[0]
                        event_content = event_data[1]
                        return event_name, event_content
            elif packet_type == 4:  # ERROR
                return 'error', data
            
            return 'unknown', data
            
        except Exception as e:
            return 'raw', message
    
    def _on_message(self, ws, message):
        """Handle incoming messages"""
        self.stats['messages_received'] += 1
        
        if self.socketio_mode:
            event_name, data = self._parse_socketio_message(message)
            
            if event_name == 'connect':
                self._on_socketio_connect(data)
            elif event_name == 'disconnect':
                self._on_socketio_disconnect(data)
            elif event_name == 'sensor_update':
                self._handle_sensor_update(data)
            elif event_name == 'notification':
                self._handle_notification(data)
            elif event_name == 'actuator_update':
                self._handle_actuator_update(data)
            elif event_name == 'connected':
                self._handle_connected(data)
            elif event_name == 'message':
                # Handle raw message
                self._handle_raw_message(data)
            elif event_name == 'error':
                self._handle_error(data)
            else:
                # Unknown event
                print(f"\n{Fore.YELLOW}Unknown event '{event_name}': {data}{Style.RESET_ALL}")
        else:
            # Raw WebSocket mode
            try:
                data = json.loads(message)
                self._handle_raw_message(data)
            except json.JSONDecodeError:
                print(f"\n{Fore.YELLOW}Raw: {message}{Style.RESET_ALL}")
    
    def _on_socketio_connect(self, data):
        """Handle Socket.IO connection"""
        print(f"{Fore.GREEN}✓ Socket.IO Connected{Style.RESET_ALL}")
    
    def _on_socketio_disconnect(self, data):
        """Handle Socket.IO disconnection"""
        print(f"\n{Fore.YELLOW}✗ Socket.IO Disconnected{Style.RESET_ALL}")
    
    def _handle_sensor_update(self, data):
        """Handle sensor update from server"""
        self.stats['sensor_updates'] += 1
        
        sensor_type = data.get('sensor_type')
        value = data.get('value')
        unit = data.get('unit', '')
        timestamp = data.get('timestamp')
        device_id = data.get('device_id', 'unknown')
        
        if sensor_type in self.sensor_data:
            self.sensor_data[sensor_type] = {
                'value': value,
                'unit': unit,
                'timestamp': timestamp,
                'device_id': device_id
            }
            self.history[sensor_type].append({
                'value': value,
                'timestamp': timestamp,
                'unit': unit
            })
            self._update_display()
    
    def _handle_notification(self, data):
        """Handle notification from server"""
        msg_type = data.get('type', 'info')
        message = data.get('message', '')
        
        color = Fore.YELLOW if msg_type == 'warning' else Fore.CYAN if msg_type == 'info' else Fore.GREEN
        print(f"\n{color}[NOTIFICATION] {message}{Style.RESET_ALL}")
    
    def _handle_actuator_update(self, data):
        """Handle actuator status update"""
        device_id = data.get('device_id')
        actuator = data.get('actuator')
        status = data.get('status')
        
        print(f"\n{Fore.BLUE}[ACTUATOR] {device_id}/{actuator}: {status}{Style.RESET_ALL}")
    
    def _handle_connected(self, data):
        """Handle connection confirmation"""
        client_id = data.get('client_id')
        print(f"{Fore.GREEN}✓ Server confirmed connection (Client: {client_id}){Style.RESET_ALL}")
    
    def _handle_raw_message(self, data):
        """Handle raw JSON message"""
        print(f"\n{Fore.YELLOW}Message: {json.dumps(data, indent=2)}{Style.RESET_ALL}")
    
    def _handle_error(self, data):
        """Handle error message"""
        print(f"\n{Fore.RED}Error: {data}{Style.RESET_ALL}")
    
    def _update_display(self):
        """Update the display with latest sensor data"""
        # Clear screen
        print('\033[2J\033[H', end='')
        
        # Header
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}IoT Hidroponik - Real-time Sensor Monitor{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"URL: {self.base_url}")
        print(f"Mode: {'Socket.IO' if self.socketio_mode else 'Raw WebSocket'}")
        if self.stats['connection_time']:
            duration = datetime.now() - self.stats['connection_time']
            print(f"Connected: {duration.seconds} seconds")
        print(f"Messages: {self.stats['messages_received']} | Sensor Updates: {self.stats['sensor_updates']}")
        print(f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Fore.CYAN}{'-'*70}{Style.RESET_ALL}")
        
        # Sensor values
        for sensor, data in self.sensor_data.items():
            value = data.get('value')
            unit = data.get('unit', '')
            timestamp = data.get('timestamp')
            device_id = data.get('device_id', '')
            
            if value is not None:
                # Color coding based on sensor ranges
                if sensor == 'ph':
                    color = Fore.GREEN if 6.0 <= value <= 7.5 else Fore.RED
                    unit_display = ''
                    value_display = f"{value:.1f}"
                elif sensor == 'tds':
                    color = Fore.GREEN if value <= 1000 else Fore.RED
                    unit_display = 'ppm'
                    value_display = f"{value:.0f}"
                elif sensor == 'suhu':
                    color = Fore.GREEN if 20 <= value <= 30 else Fore.RED
                    unit_display = '°C'
                    value_display = f"{value:.1f}"
                elif sensor == 'kelembapan':
                    color = Fore.GREEN if 50 <= value <= 80 else Fore.RED
                    unit_display = '%'
                    value_display = f"{value:.0f}"
                else:
                    color = Fore.WHITE
                    unit_display = unit
                    value_display = str(value)
                
                # Format display
                sensor_name = sensor.upper()
                if unit_display:
                    value_str = f"{value_display} {unit_display}"
                else:
                    value_str = value_display
                
                # Device info
                device_info = f"[{device_id}]" if device_id else ""
                
                print(f"{Fore.WHITE}{sensor_name:12}{Style.RESET_ALL}: {color}{value_str:>12}{Style.RESET_ALL} {device_info}")
                if timestamp:
                    # Show only time part
                    time_part = timestamp.split('T')[1][:8] if 'T' in timestamp else timestamp
                    print(f"             {Fore.BLACK}{time_part}{Style.RESET_ALL}")
            else:
                print(f"{Fore.WHITE}{sensor.upper():12}{Style.RESET_ALL}: {Fore.YELLOW}Waiting...{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}{'-'*70}{Style.RESET_ALL}")
        
        # Mini graph for pH (if data available)
        if self.history['ph'] and len(self.history['ph']) > 1:
            print(f"\n{Fore.WHITE}pH Trend (last 20 readings):{Style.RESET_ALL}")
            self._draw_mini_graph(self.history['ph'], min_val=6.0, max_val=7.5, width=60)
        
        # Mini graph for suhu (if data available)
        if self.history['suhu'] and len(self.history['suhu']) > 1:
            print(f"\n{Fore.WHITE}Suhu Trend (last 20 readings):{Style.RESET_ALL}")
            self._draw_mini_graph(self.history['suhu'], min_val=20, max_val=35, width=60)
        
        # Footer
        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Press Ctrl+C to exit{Style.RESET_ALL}")
    
    def _draw_mini_graph(self, data, min_val=None, max_val=None, width=50):
        """Draw a mini graph with color coding"""
        if not data:
            return
        
        values = [d['value'] for d in data[-20:]]
        if not values:
            return
        
        if min_val is None:
            min_val = min(values)
        if max_val is None:
            max_val = max(values)
        
        if max_val == min_val:
            max_val = min_val + 1
        
        for val in values[-20:]:
            normalized = (val - min_val) / (max_val - min_val)
            bar_length = int(normalized * width)
            bar = '█' * bar_length + '░' * (width - bar_length)
            
            # Color based on value position
            if val < (min_val + (max_val - min_val) * 0.33):
                color = Fore.GREEN
            elif val < (min_val + (max_val - min_val) * 0.66):
                color = Fore.YELLOW
            else:
                color = Fore.RED
            
            print(f"  {color}{bar}{Style.RESET_ALL} {val:.1f}")
    
    def _on_error(self, ws, error):
        """Handle WebSocket error"""
        print(f"\n{Fore.RED}Error: {error}{Style.RESET_ALL}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close"""
        print(f"\n{Fore.YELLOW}Disconnected{Style.RESET_ALL}")
        self.connected = False
        self.running = False
    
    def _on_open(self, ws):
        """Handle WebSocket open"""
        print(f"{Fore.GREEN}Connected to {self.url}{Style.RESET_ALL}")
        self.connected = True
        self.stats['connection_time'] = datetime.now()
        
        # Send Socket.IO connect packet if in Socket.IO mode
        if self.socketio_mode:
            ws.send("0")  # Socket.IO connect packet
            time.sleep(0.1)
    
    def run(self):
        """Run the monitor"""
        websocket.enableTrace(False)
        
        self.ws = websocket.WebSocketApp(
            self.url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
        
        try:
            self.ws.run_forever()
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Stopping monitor...{Style.RESET_ALL}")
            if self.ws:
                self.ws.close()
        except Exception as e:
            print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='WebSocket Monitor for IoT Hidroponik',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Monitor with Socket.IO mode (default)
  python websocket_monitor.py ws://localhost:5000
  
  # Monitor with raw WebSocket mode
  python websocket_monitor.py ws://localhost:5000 --raw
  
  # Monitor custom URL
  python websocket_monitor.py ws://192.168.1.100:5000
        """
    )
    parser.add_argument('url', nargs='?', default='ws://localhost:5000',
                       help='WebSocket base URL (default: ws://localhost:5000)')
    parser.add_argument('-r', '--raw', action='store_true',
                       help='Use raw WebSocket mode (without Socket.IO protocol)')
    
    args = parser.parse_args()
    
    # Validate URL
    if not args.url.startswith('ws://') and not args.url.startswith('wss://'):
        print(f"{Fore.RED}Error: URL must start with ws:// or wss://{Style.RESET_ALL}")
        sys.exit(1)
    
    print(f"{Fore.CYAN}Starting WebSocket Monitor...{Style.RESET_ALL}")
    print(f"{Fore.CYAN}URL: {args.url}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Mode: {'Raw WebSocket' if args.raw else 'Socket.IO'}{Style.RESET_ALL}")
    print()
    
    monitor = WebSocketMonitor(args.url, socketio_mode=not args.raw)
    monitor.run()


if __name__ == "__main__":
    main()