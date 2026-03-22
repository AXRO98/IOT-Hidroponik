#!/usr/bin/env python3
"""
File        : websocket_benchmark.py
Author      : Keyfin Agustio Suratman
Description : WebSocket Benchmark for performance testing
Created     : 2026-03-23
"""

import sys
import json
import time
import threading
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


class WebSocketBenchmark:
    """Benchmark WebSocket performance"""
    
    def __init__(self, url: str, num_clients: int = 1, message_rate: int = 10):
        self.url = url
        self.socketio_mode = True
        self.num_clients = num_clients
        self.message_rate = message_rate
        self.clients = []
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'errors': 0,
            'latencies': deque(maxlen=1000)
        }
        self.running = True
        self.lock = threading.Lock()

        # Jika menggunakan Socket.IO, tambahkan path dan query parameters
        if self.socketio_mode:
            # Socket.IO WebSocket URL format: ws://host:port/socket.io/?EIO=4&transport=websocket
            parsed = urllib.parse.urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            self.url = f"{base_url}/socket.io/?EIO=4&transport=websocket"
        else:
            self.url = url

    def _on_message(self, client_id, start_time):
        """Handle message with latency tracking"""
        latency = (time.time() - start_time) * 1000  # ms
        with self.lock:
            self.stats['messages_received'] += 1
            self.stats['latencies'].append(latency)
    
    def _on_error(self, client_id, error):
        """Handle error"""
        with self.lock:
            self.stats['errors'] += 1
        print(f"{Fore.RED}Client {client_id} error: {error}{Style.RESET_ALL}")
    
    def _send_messages(self, client_id, ws):
        """Send messages at specified rate"""
        while self.running:
            start_time = time.time()
            
            try:
                message = {
                    'type': 'ping',
                    'content': {
                        'client_id': client_id,
                        'timestamp': datetime.now().isoformat(),
                        'counter': self.stats['messages_sent'] + 1
                    }
                }
                ws.send(json.dumps(message))
                
                with self.lock:
                    self.stats['messages_sent'] += 1
                
                # Wait for next message
                time.sleep(1.0 / self.message_rate)
                
            except Exception as e:
                with self.lock:
                    self.stats['errors'] += 1
                print(f"{Fore.RED}Client {client_id} send error: {e}{Style.RESET_ALL}")
                break
    
    def _run_client(self, client_id):
        """Run a single client"""
        try:
            ws = websocket.WebSocket()
            ws.connect(self.url)
            
            print(f"{Fore.GREEN}Client {client_id} connected{Style.RESET_ALL}")
            
            # Start sending messages in separate thread
            send_thread = threading.Thread(
                target=self._send_messages,
                args=(client_id, ws)
            )
            send_thread.daemon = True
            send_thread.start()
            
            # Receive messages
            while self.running:
                try:
                    message = ws.recv()
                    if message:
                        # Parse message to get timestamp for latency
                        try:
                            data = json.loads(message)
                            if data.get('type') == 'pong':
                                # Calculate latency
                                pass
                        except:
                            pass
                        
                        with self.lock:
                            self.stats['messages_received'] += 1
                            
                except websocket.WebSocketConnectionClosedException:
                    break
                except Exception as e:
                    with self.lock:
                        self.stats['errors'] += 1
                    break
            
            ws.close()
            print(f"{Fore.YELLOW}Client {client_id} disconnected{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}Client {client_id} failed: {e}{Style.RESET_ALL}")
            with self.lock:
                self.stats['errors'] += 1
    
    def run(self, duration: int = 60):
        """Run benchmark for specified duration"""
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}WebSocket Benchmark{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"URL: {self.url}")
        print(f"Clients: {self.num_clients}")
        print(f"Message Rate: {self.message_rate} msg/sec/client")
        print(f"Duration: {duration} seconds")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        # Start clients
        threads = []
        for i in range(self.num_clients):
            t = threading.Thread(target=self._run_client, args=(i,))
            t.daemon = True
            t.start()
            threads.append(t)
            time.sleep(0.1)  # Stagger start
        
        # Run for duration
        start_time = time.time()
        last_report = start_time
        
        try:
            while time.time() - start_time < duration:
                time.sleep(1)
                
                now = time.time()
                if now - last_report >= 5:  # Report every 5 seconds
                    elapsed = now - start_time
                    with self.lock:
                        sent = self.stats['messages_sent']
                        received = self.stats['messages_received']
                        errors = self.stats['errors']
                        latencies = list(self.stats['latencies'])
                    
                    print(f"\n{Fore.CYAN}[{elapsed:.0f}s] Progress:{Style.RESET_ALL}")
                    print(f"  Messages Sent: {sent}")
                    print(f"  Messages Received: {received}")
                    print(f"  Errors: {errors}")
                    
                    if latencies:
                        avg_latency = sum(latencies) / len(latencies)
                        min_latency = min(latencies)
                        max_latency = max(latencies)
                        print(f"  Avg Latency: {avg_latency:.2f} ms")
                        print(f"  Min Latency: {min_latency:.2f} ms")
                        print(f"  Max Latency: {max_latency:.2f} ms")
                    
                    last_report = now
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Benchmark interrupted{Style.RESET_ALL}")
        
        finally:
            self.running = False
            time.sleep(2)  # Wait for cleanup
            
            # Final report
            print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Benchmark Results{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
            print(f"Total Messages Sent: {self.stats['messages_sent']}")
            print(f"Total Messages Received: {self.stats['messages_received']}")
            print(f"Total Errors: {self.stats['errors']}")
            
            latencies = list(self.stats['latencies'])
            if latencies:
                print(f"\nLatency Statistics:")
                print(f"  Average: {sum(latencies) / len(latencies):.2f} ms")
                print(f"  Min: {min(latencies):.2f} ms")
                print(f"  Max: {max(latencies):.2f} ms")
                print(f"  95th Percentile: {sorted(latencies)[int(len(latencies)*0.95)]:.2f} ms")
            
            # Calculate throughput
            duration_actual = time.time() - start_time
            throughput_sent = self.stats['messages_sent'] / duration_actual
            throughput_received = self.stats['messages_received'] / duration_actual
            print(f"\nThroughput:")
            print(f"  Sent: {throughput_sent:.2f} msg/sec")
            print(f"  Received: {throughput_received:.2f} msg/sec")
            print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(description='WebSocket Benchmark')
    parser.add_argument('url', nargs='?', default='ws://localhost:5000',
                       help='WebSocket URL (default: ws://localhost:5000)')
    parser.add_argument('-c', '--clients', type=int, default=1,
                       help='Number of concurrent clients (default: 1)')
    parser.add_argument('-r', '--rate', type=int, default=10,
                       help='Message rate per client (msg/sec, default: 10)')
    parser.add_argument('-d', '--duration', type=int, default=60,
                       help='Test duration in seconds (default: 60)')
    
    args = parser.parse_args()
    
    benchmark = WebSocketBenchmark(args.url, args.clients, args.rate)
    benchmark.run(args.duration)


if __name__ == "__main__":
    main()