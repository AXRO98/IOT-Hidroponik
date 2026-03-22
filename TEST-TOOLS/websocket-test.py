#!/usr/bin/env python3
"""
File        : websocket_tester.py
Author      : Keyfin Agustio Suratman
Description : WebSocket Tester untuk IoT Hidroponik (dengan dukungan Socket.IO)
Created     : 2026-03-23
"""

import sys
import json
import time
import argparse
import threading
import urllib.parse
from datetime import datetime
from typing import Optional, Dict, Any

try:
    import websocket
    from colorama import init, Fore, Style
    init()  # Initialize colorama
except ImportError:
    print("Please install required packages:")
    print("pip install websocket-client colorama")
    sys.exit(1)


class WebSocketTester:
    """WebSocket tester untuk IoT Hidroponik dengan Socket.IO support"""
    
    def __init__(self, url: str, verbose: bool = True, auto_reconnect: bool = True, socketio_mode: bool = True):
        """
        Initialize WebSocket tester
        
        Args:
            url: WebSocket URL (ws:// or wss://)
            verbose: Print detailed logs
            auto_reconnect: Auto reconnect on disconnect
            socketio_mode: Use Socket.IO protocol
        """
        self.base_url = url
        self.verbose = verbose
        self.auto_reconnect = auto_reconnect
        self.socketio_mode = socketio_mode
        self.ws = None
        self.connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.running = True
        self.received_messages = []
        self.stats = {
            'messages_received': 0,
            'messages_sent': 0,
            'connection_time': None,
            'disconnection_time': None
        }
        
        # Jika menggunakan Socket.IO, tambahkan path dan query parameters
        if self.socketio_mode:
            # Socket.IO WebSocket URL format: ws://host:port/socket.io/?EIO=4&transport=websocket
            parsed = urllib.parse.urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            self.url = f"{base_url}/socket.io/?EIO=4&transport=websocket"
        else:
            self.url = url
        
        # Colors for different message types
        self.colors = {
            'info': Fore.CYAN,
            'success': Fore.GREEN,
            'error': Fore.RED,
            'warning': Fore.YELLOW,
            'message': Fore.WHITE,
            'sensor': Fore.MAGENTA,
            'actuator': Fore.BLUE,
            'notification': Fore.YELLOW
        }
    
    def _log(self, msg: str, level: str = 'info'):
        """Print colored log message"""
        if not self.verbose:
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = self.colors.get(level, Fore.WHITE)
        
        if level == 'success':
            print(f"{color}[{timestamp}] ✓ {msg}{Style.RESET_ALL}")
        elif level == 'error':
            print(f"{color}[{timestamp}] ✗ {msg}{Style.RESET_ALL}")
        elif level == 'warning':
            print(f"{color}[{timestamp}] ⚠ {msg}{Style.RESET_ALL}")
        else:
            print(f"{color}[{timestamp}] ℹ {msg}{Style.RESET_ALL}")
    
    def _parse_socketio_message(self, message):
        """Parse Socket.IO protocol message"""
        # Socket.IO message format: <packet_type>[data]
        # 0 = CONNECT, 1 = DISCONNECT, 2 = EVENT, 3 = ACK, 4 = ERROR, 5 = BINARY_EVENT, 6 = BINARY_ACK
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
                # Event format: "[\"event_name\",{...}]"
                if data:
                    event_data = json.loads(data)
                    if isinstance(event_data, list) and len(event_data) >= 2:
                        event_name = event_data[0]
                        event_content = event_data[1]
                        return event_name, event_content
            elif packet_type == 3:  # ACK
                return 'ack', data
            elif packet_type == 4:  # ERROR
                return 'error', data
            
            return 'unknown', data
            
        except Exception as e:
            return 'raw', message
    
    def _on_message(self, ws, message):
        """Handle incoming message"""
        self.stats['messages_received'] += 1
        self.received_messages.append({
            'timestamp': datetime.now(),
            'data': message
        })
        
        # Keep only last 100 messages
        if len(self.received_messages) > 100:
            self.received_messages = self.received_messages[-100:]
        
        # Parse Socket.IO message if needed
        if self.socketio_mode:
            event_name, data = self._parse_socketio_message(message)
            
            if event_name == 'connect':
                self._log(f"Socket.IO Connected", 'success')
                return
            elif event_name == 'disconnect':
                self._log(f"Socket.IO Disconnected", 'warning')
                return
            elif event_name == 'message':
                # Handle regular message
                self._handle_json_message(data)
            elif event_name and data:
                # Handle event
                self._handle_json_message({event_name: data})
            else:
                self._log(f"Raw Socket.IO message: {message[:100]}", 'message')
        else:
            # Raw WebSocket
            try:
                data = json.loads(message)
                self._handle_json_message(data)
            except json.JSONDecodeError:
                self._log(f"Message: {message[:100]}", 'message')
                print(f"   {Fore.WHITE}{message}{Style.RESET_ALL}")
    
    def _handle_json_message(self, data):
        """Handle JSON message"""
        if isinstance(data, dict):
            event = data.get('event', data.get('type', 'unknown'))
            
            # Color based on event type
            if 'sensor' in event or 'update' in event:
                self._log(f"📊 {event}", 'sensor')
                print(f"   {Fore.MAGENTA}{json.dumps(data, indent=2)}{Style.RESET_ALL}")
            elif 'actuator' in event or 'command' in event:
                self._log(f"🔧 {event}", 'actuator')
                print(f"   {Fore.BLUE}{json.dumps(data, indent=2)}{Style.RESET_ALL}")
            elif 'notification' in event:
                self._log(f"🔔 {event}", 'notification')
                print(f"   {Fore.YELLOW}{json.dumps(data, indent=2)}{Style.RESET_ALL}")
            else:
                self._log(f"📨 {event}", 'message')
                print(f"   {Fore.WHITE}{json.dumps(data, indent=2)}{Style.RESET_ALL}")
        else:
            self._log(f"Message: {str(data)[:100]}", 'message')
            print(f"   {Fore.WHITE}{data}{Style.RESET_ALL}")
    
    def _on_error(self, ws, error):
        """Handle error"""
        self._log(f"Error: {error}", 'error')
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Handle close"""
        self.connected = False
        self.stats['disconnection_time'] = datetime.now()
        self._log(f"Disconnected (code: {close_status_code}, msg: {close_msg})", 'warning')
        
        if self.auto_reconnect and self.running:
            self._reconnect()
    
    def _on_open(self, ws):
        """Handle open"""
        self.connected = True
        self.reconnect_attempts = 0
        self.stats['connection_time'] = datetime.now()
        self._log(f"Connected to {self.url}", 'success')
        
        # Send initial Socket.IO connect message if needed
        if self.socketio_mode:
            # Send Socket.IO connect packet (type 0)
            self.ws.send("0")
            time.sleep(0.1)
        
        # Send initial ping message
        self.send_message({
            'type': 'ping',
            'content': {
                'message': 'WebSocket Tester Connected',
                'timestamp': datetime.now().isoformat()
            }
        })
    
    def _reconnect(self):
        """Reconnect with exponential backoff"""
        if not self.running:
            return
        
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            self._log(f"Max reconnection attempts reached", 'error')
            return
        
        self.reconnect_attempts += 1
        delay = min(30, 2 ** self.reconnect_attempts)
        
        self._log(f"Reconnecting in {delay} seconds (attempt {self.reconnect_attempts})", 'warning')
        time.sleep(delay)
        
        if self.running:
            self.connect()
    
    def connect(self):
        """Connect to WebSocket server"""
        try:
            # Enable WebSocket trace if verbose
            if self.verbose:
                websocket.enableTrace(False)
            
            self.ws = websocket.WebSocketApp(
                self.url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            
            # Run in separate thread
            wst = threading.Thread(target=self.ws.run_forever, daemon=True)
            wst.start()
            
            # Wait for connection
            time.sleep(1)
            
        except Exception as e:
            self._log(f"Connection failed: {e}", 'error')
            if self.auto_reconnect:
                self._reconnect()
    
    def disconnect(self):
        """Disconnect from WebSocket server"""
        self.running = False
        if self.ws:
            self.ws.close()
        self._log("Disconnected", 'info')
    
    def send_message(self, data: Dict[str, Any]):
        """Send message to WebSocket server"""
        if not self.connected:
            self._log("Not connected, cannot send message", 'error')
            return False
        
        try:
            if isinstance(data, dict):
                message = json.dumps(data)
            else:
                message = str(data)
            
            # Wrap in Socket.IO event packet if needed
            if self.socketio_mode:
                # Send as Socket.IO EVENT packet (type 2)
                # Format: 2["event_name",{...}]
                event_message = f'2["message",{message}]'
                self.ws.send(event_message)
            else:
                self.ws.send(message)
            
            self.stats['messages_sent'] += 1
            self._log(f"Sent: {message[:100]}", 'success')
            return True
            
        except Exception as e:
            self._log(f"Failed to send message: {e}", 'error')
            return False
    
    def send_sensor_request(self, device_id: str = None, sensor_type: str = None):
        """Send sensor data request"""
        content = {}
        if device_id:
            content['device_id'] = device_id
        if sensor_type:
            content['sensor_type'] = sensor_type
        
        return self.send_message({
            'type': 'sensor_request',
            'content': content
        })
    
    def send_actuator_command(self, device_id: str, actuator: str, command: str):
        """Send actuator command"""
        return self.send_message({
            'type': 'actuator_command',
            'content': {
                'device_id': device_id,
                'actuator': actuator,
                'command': command
            }
        })
    
    def send_join_room(self, room: str):
        """Join a room"""
        return self.send_message({
            'type': 'join',
            'room': room
        })
    
    def send_leave_room(self, room: str):
        """Leave a room"""
        return self.send_message({
            'type': 'leave',
            'room': room
        })
    
    def show_stats(self):
        """Show connection statistics"""
        print("\n" + "="*60)
        print(f"{Fore.CYAN}WebSocket Connection Statistics{Style.RESET_ALL}")
        print("="*60)
        print(f"URL: {self.url}")
        print(f"Connected: {self.connected}")
        if self.stats['connection_time']:
            duration = datetime.now() - self.stats['connection_time']
            print(f"Connection Duration: {duration}")
        print(f"Messages Received: {self.stats['messages_received']}")
        print(f"Messages Sent: {self.stats['messages_sent']}")
        print(f"Reconnect Attempts: {self.reconnect_attempts}")
        
        if self.received_messages:
            print(f"\n{Fore.CYAN}Last 5 Messages:{Style.RESET_ALL}")
            for msg in self.received_messages[-5:]:
                try:
                    data = json.loads(msg['data'])
                    print(f"  {msg['timestamp'].strftime('%H:%M:%S')}: {data.get('type', 'unknown')}")
                except:
                    print(f"  {msg['timestamp'].strftime('%H:%M:%S')}: {msg['data'][:50]}")
        print("="*60 + "\n")
    
    def interactive_mode(self):
        """Interactive command mode"""
        print("\n" + "="*60)
        print(f"{Fore.CYAN}Interactive WebSocket Tester{Style.RESET_ALL}")
        print("="*60)
        print(f"Mode: {'Socket.IO' if self.socketio_mode else 'Raw WebSocket'}")
        print(f"URL: {self.base_url}")
        print("\nCommands:")
        print("  stats          - Show statistics")
        print("  sensor [id]    - Request sensor data")
        print("  actuator <id> <act> <cmd> - Send actuator command")
        print("  join <room>    - Join a room")
        print("  leave <room>   - Leave a room")
        print("  send <json>    - Send custom JSON message")
        print("  clear          - Clear screen")
        print("  help           - Show this help")
        print("  quit/exit      - Exit tester")
        print("="*60 + "\n")
        
        while self.running:
            try:
                cmd = input(f"{Fore.GREEN}websocket> {Style.RESET_ALL}").strip()
                
                if not cmd:
                    continue
                
                parts = cmd.split()
                command = parts[0].lower()
                
                if command == 'quit' or command == 'exit':
                    self.disconnect()
                    break
                
                elif command == 'stats':
                    self.show_stats()
                
                elif command == 'sensor':
                    device_id = parts[1] if len(parts) > 1 else None
                    self.send_sensor_request(device_id)
                
                elif command == 'actuator':
                    if len(parts) >= 4:
                        _, device_id, actuator, command_str = parts[:4]
                        self.send_actuator_command(device_id, actuator, command_str)
                    else:
                        print("Usage: actuator <device_id> <actuator> <command>")
                
                elif command == 'join':
                    if len(parts) >= 2:
                        self.send_join_room(parts[1])
                    else:
                        print("Usage: join <room>")
                
                elif command == 'leave':
                    if len(parts) >= 2:
                        self.send_leave_room(parts[1])
                    else:
                        print("Usage: leave <room>")
                
                elif command == 'send':
                    if len(parts) >= 2:
                        try:
                            json_data = json.loads(' '.join(parts[1:]))
                            self.send_message(json_data)
                        except json.JSONDecodeError:
                            print("Invalid JSON format")
                    else:
                        print("Usage: send <json>")
                
                elif command == 'clear':
                    import os
                    os.system('cls' if os.name == 'nt' else 'clear')
                    self.interactive_mode()
                
                elif command == 'help':
                    print("\nCommands:")
                    print("  stats          - Show statistics")
                    print("  sensor [id]    - Request sensor data")
                    print("  actuator <id> <act> <cmd> - Send actuator command")
                    print("  join <room>    - Join a room")
                    print("  leave <room>   - Leave a room")
                    print("  send <json>    - Send custom JSON message")
                    print("  clear          - Clear screen")
                    print("  help           - Show this help")
                    print("  quit/exit      - Exit tester\n")
                
                else:
                    print(f"Unknown command: {command}. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\n")
                self.disconnect()
                break
            except Exception as e:
                print(f"Error: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='WebSocket Tester for IoT Hidroponik')
    parser.add_argument('url', nargs='?', default='ws://localhost:5000',
                       help='WebSocket URL (default: ws://localhost:5000)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Quiet mode (no verbose output)')
    parser.add_argument('-c', '--command', type=str,
                       help='Send a single command and exit')
    parser.add_argument('-i', '--interactive', action='store_true',
                       help='Start interactive mode')
    parser.add_argument('-t', '--test', action='store_true',
                       help='Run connection test and exit')
    parser.add_argument('-r', '--raw', action='store_true',
                       help='Use raw WebSocket (without Socket.IO protocol)')
    
    args = parser.parse_args()
    
    # Determine verbose mode
    verbose = not args.quiet and (args.verbose or args.interactive or not args.command)
    
    # Create tester (default use Socket.IO mode)
    tester = WebSocketTester(args.url, verbose=verbose, socketio_mode=not args.raw)
    
    # Connect
    tester.connect()
    time.sleep(2)  # Wait for connection
    
    if not tester.connected and args.test:
        print(f"{Fore.RED}Connection failed!{Style.RESET_ALL}")
        sys.exit(1)
    
    # Handle different modes
    if args.test:
        # Test mode
        print(f"{Fore.GREEN}Connection test successful!{Style.RESET_ALL}")
        tester.show_stats()
        tester.disconnect()
        time.sleep(1)
        
    elif args.command:
        # Single command mode
        try:
            if args.command.startswith('{'):
                # JSON command
                data = json.loads(args.command)
                tester.send_message(data)
            else:
                # Parse command
                parts = args.command.split()
                cmd = parts[0].lower()
                
                if cmd == 'sensor':
                    device_id = parts[1] if len(parts) > 1 else None
                    tester.send_sensor_request(device_id)
                elif cmd == 'actuator' and len(parts) >= 4:
                    tester.send_actuator_command(parts[1], parts[2], parts[3])
                elif cmd == 'join' and len(parts) >= 2:
                    tester.send_join_room(parts[1])
                elif cmd == 'leave' and len(parts) >= 2:
                    tester.send_leave_room(parts[1])
                else:
                    print(f"Unknown command: {cmd}")
            
            # Wait a bit for response
            time.sleep(2)
            tester.disconnect()
            
        except Exception as e:
            print(f"Error: {e}")
            tester.disconnect()
            
    else:
        # Interactive mode
        try:
            tester.interactive_mode()
        except KeyboardInterrupt:
            print("\n")
        finally:
            tester.disconnect()
            time.sleep(1)


if __name__ == "__main__":
    main()