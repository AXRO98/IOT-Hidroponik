"""
Module      : apps.services.mqtt_connect
Author      : Keyfin Suratman
Description : MQTT Client untuk koneksi ke broker
Created     : 2026-03-23
Updated     : 2026-03-25
"""

import paho.mqtt.client as mqtt
import json
import threading
import ssl
from flask import current_app

# Import MQTT specific logger
from apps.utils import log_mqtt, log_info, log_success, log_warning, log_error
from apps.services.mqtt_service import process_sensor_data


class MQTTClient:
    """
    MQTT Client untuk koneksi ke broker.
    
    Kelas ini mengelola koneksi MQTT, subscribe/publish message, 
    serta penanganan reconnect otomatis dengan exponential backoff.
    
    Attributes:
        client (mqtt.Client): Instance client paho-mqtt
        app (Flask): Instance aplikasi Flask
        connected (bool): Status koneksi MQTT
        subscribed_topics (list): Daftar topic yang telah disubscribe
        broker_url (str): URL broker MQTT
        broker_port (int): Port broker MQTT
        keepalive (int): Keepalive interval dalam detik
        reconnect_delay (int): Delay awal reconnect dalam detik
        max_reconnect_delay (int): Delay maksimum reconnect dalam detik
        reconnect_enabled (bool): Flag untuk mengaktifkan/menonaktifkan reconnect
        status_auth (str): Status autentikasi ('invalid_credentials' atau kosong)
        invalid_logged (bool): Flag untuk mencegah log berulang
        topic_all (str): Topic untuk subscribe semua sensor
        topic_temp (str): Topic khusus temperature
    """
    
    def __init__(self, app=None):
        """
        Inisialisasi objek MQTTClient.
        
        Constructor akan menginisialisasi atribut dasar dan
        memanggil init_app() jika parameter app diberikan.
        
        Args:
            app (Flask, optional): Instance aplikasi Flask. Defaults to None.
        """
        self.client = None
        self.app = None
        self.connected = False

        self.broker_url = None
        self.broker_port = None
        self.keepalive = None

        self.reconnect_delay = 5
        self.max_reconnect_delay = 60

        self.reconnect_enabled = True
        self.status_auth = ''
        self.invalid_logged = False

        # topic default (belum ada app)
        self.topic_sensor = None

        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """
        Inisialisasi client MQTT dengan konfigurasi dari aplikasi Flask.
        
        Method ini mengambil konfigurasi MQTT dari app.config,
        membuat instance client paho-mqtt, mengatur credentials,
        TLS/SSL, callback functions, dan memulai koneksi.
        
        Args:
            app (Flask): Instance aplikasi Flask yang berisi konfigurasi MQTT
            
        Konfigurasi yang dibaca dari app.config:
            - MQTT_TOPIC_ALL: Topic untuk subscribe semua sensor
            - MQTT_TOPIC_TEMPERATURE: Topic khusus temperature
            - MQTT_BROKER_URL: URL broker MQTT
            - MQTT_BROKER_PORT: Port broker MQTT
            - MQTT_KEEPALIVE: Keepalive interval
            - MQTT_CONFIG: Dictionary konfigurasi tambahan
            - MQTT_USERNAME: Username untuk autentikasi
            - MQTT_PASSWORD: Password untuk autentikasi
            - MQTT_CLIENT_ID: Client ID untuk identifikasi
        """
        self.app = app

        # Ambil config DI SINI (bukan di __init__)
        self.broker_url = app.config.get('MQTT_BROKER_URL')
        self.broker_port = app.config.get('MQTT_BROKER_PORT')
        self.keepalive = app.config.get('MQTT_KEEPALIVE')
        self.topic_sensor = app.config.get('MQTT_TOPIC_SENSOR')

        # Credentials
        username = app.config.get('username') or app.config.get('MQTT_USERNAME')
        password = app.config.get('password') or app.config.get('MQTT_PASSWORD')

        # Client ID
        client_id = app.config.get('MQTT_CLIENT_ID')
        
        # Buat MQTT client
        self.client = mqtt.Client(client_id=client_id)

        # Set username/password jika ada
        if username and password:
            self.client.username_pw_set(username, password)
            log_info(f"MQTT credentials set for user: {username}")
        
        # Setup TLS jika port 8883 (HiveMQ Cloud)
        if self.broker_port == 8883:
            log_info(f"Setting up TLS for port {self.broker_port}...")
            self.client.tls_set(cert_reqs=ssl.CERT_NONE)
            self.client.tls_insecure_set(True)
        
        # Set callback functions
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_publish = self._on_publish
        self.client.on_disconnect = self._on_disconnect
        self.client.on_log = self._on_log
        
        # Start connection in background thread
        self._start_loop()
    
    def _on_connect(self, client, userdata, flags, rc):
        """
        Callback internal yang dipanggil saat client mencoba connect ke broker.
        
        Method ini akan dipanggil oleh paho-mqtt ketika proses koneksi
        selesai (baik sukses maupun gagal).
        
        Args:
            client (mqtt.Client): Instance client MQTT
            userdata (any): Data pengguna yang diteruskan dari client
            flags (dict): Response flags dari broker
            rc (int): Return code dari broker:
                0 = Connection successful
                1 = Connection refused - incorrect protocol version
                2 = Connection refused - invalid client identifier
                3 = Connection refused - server unavailable
                4 = Connection refused - bad username or password
                5 = Connection refused - not authorised
                
        Behavior:
            - Jika sukses (rc==0): set connected=True, reset reconnect_delay,
              subscribe ke topic sensor
            - Jika gagal karena kredensial (rc==4/5): matikan reconnect,
              hentikan loop client
            - Jika gagal alasan lain: set connected=False, tampilkan error
        """
        if rc == 0:
            self.connected = True
            self.reconnect_delay = 5
            self.reconnect_enabled = True
            self.subscribe(self.topic_sensor)  # Subscribe ke semua topic sensor
            log_mqtt("CONNECTED", f"{self.broker_url}:{self.broker_port}", "Connection successful")
        else:
            error_messages = {
                1: "Connection refused - incorrect protocol version",
                2: "Connection refused - invalid client identifier",
                3: "Connection refused - server unavailable",
                4: "Connection refused - bad username or password",
                5: "Connection refused - not authorised"
            }
            error_msg = error_messages.get(rc, f"Unknown error (code: {rc})")

            # ini kode error untuk selain auth
            log_error(f"Failed to connect to MQTT broker: {error_msg}")
            log_mqtt("ERROR", f"{self.broker_url}:{self.broker_port}", error_msg)

            # Khusus error kode 4/5 karena itu gagal auth
            if rc in [4, 5]:
                self.status_auth = 'invalid_credentials'
                self.reconnect_enabled = False  # Matikan reconnect
                if not self.invalid_logged:
                    log_error(f"MQTT loop stopped: invalid credentials for {self.broker_url}:{self.broker_port}")
                    log_mqtt("ERROR", f"{self.broker_url}:{self.broker_port}", "Invalid username/password - check .env")
                    self.invalid_logged = True
                # Hentikan loop client agar tidak ada percobaan lagi
                if self.client:
                    self.client.loop_stop()
            self.connected = False
    
    def _on_message(self, client, userdata, msg):
        """
        Callback saat menerima pesan dari MQTT broker.
        """
        topic = msg.topic

        try:
            payload_raw = msg.payload.decode('utf-8')

            try:
                # Parse JSON
                parsed_data = json.loads(payload_raw)

                # Pastikan dictionary
                if not isinstance(parsed_data, dict):
                    parsed_data = {"value": parsed_data}

            except json.JSONDecodeError:
                log_warning(f"Non-JSON payload received: {payload_raw}")
                parsed_data = {"value": payload_raw}

            # Proses data
            with self.app.app_context():
                process_sensor_data(parsed_data)

        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            log_error(error_msg)
            log_mqtt("ERROR", topic, error_msg)
    
    def _on_publish(self, client, userdata, mid):
        """
        Callback internal yang dipanggil saat publish berhasil.
        
        Method ini dipanggil setelah client berhasil mengirim pesan
        ke broker dan mendapatkan acknowledgment (untuk QoS > 0).
        
        Args:
            client (mqtt.Client): Instance client MQTT
            userdata (any): Data pengguna yang diteruskan dari client
            mid (int): Message ID dari pesan yang dipublish
        """
        log_mqtt("PUB-ACK", f"mid:{mid}", "Message published successfully")
    
    def _on_disconnect(self, client, userdata, rc):
        """
        Callback internal yang dipanggil saat client terputus dari broker.
        
        Method ini menangani logika setelah disconnect, termasuk
        penjadwalan reconnect dengan exponential backoff.
        
        Args:
            client (mqtt.Client): Instance client MQTT
            userdata (any): Data pengguna yang diteruskan dari client
            rc (int): Return code:
                0 = Clean disconnect (initiated by client)
                Lainnya = Unexpected disconnect
                
        Behavior:
            - Set connected = False
            - Jika disconnect karena kredensial invalid (rc==4/5):
              hentikan reconnect, log error sekali saja
            - Jika unexpected disconnect dan reconnect enabled:
              jadwalkan reconnect dengan delay yang meningkat
              (delay awal 5 detik, maksimal 60 detik)
        """
        if rc == 0:
            log_info("Disconnected from MQTT broker (clean disconnect)")
            log_mqtt("DISCONNECT", f"{self.broker_url}:{self.broker_port}", "Clean disconnect")
        else:
            if rc == 4 or rc == 5:
                log_error(f"Disconnected from MQTT broker due to invalid credentials (code: {rc})")
            else:
                log_warning(f"Unexpected disconnect from MQTT broker (code: {rc})")
                log_mqtt("ERROR", f"{self.broker_url}:{self.broker_port}", f"Unexpected disconnect (code: {rc})")

        self.connected = False

        # Jangan lakukan reconnect jika kredensial tidak valid atau reconnect dinonaktifkan
        if self.status_auth == 'invalid_credentials' or not self.reconnect_enabled:
            log_info("Reconnect disabled due to invalid credentials")
            return

        # Jika disconnect tidak bersih, coba reconnect dengan backoff
        if rc != 0:
            log_info(f"Attempting to reconnect in {self.reconnect_delay} seconds...")
            threading.Timer(self.reconnect_delay, self._start_loop).start()
            self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)

    
    def _on_log(self, client, userdata, level, buf):
        """
        Callback untuk logging internal paho-mqtt.
        
        Method ini menangkap log dari library paho-mqtt dan
        meneruskannya ke sistem logging aplikasi.
        
        Args:
            client (mqtt.Client): Instance client MQTT
            userdata (any): Data pengguna yang diteruskan dari client
            level (int): Level logging MQTT:
                1 = MQTT_LOG_INFO
                2 = MQTT_LOG_NOTICE
                4 = MQTT_LOG_WARNING
                8 = MQTT_LOG_ERR
                16 = MQTT_LOG_DEBUG
            buf (str): Pesan log
        """
        if level <= 1:  # MQTT_LOG_INFO
            log_mqtt("DEBUG", "paho", buf)
    
    def _start_loop(self):
        """
        Memulai MQTT loop dalam background thread.
        
        Method ini melakukan koneksi ke broker dan memulai
        loop MQTT di background thread. Jika gagal, akan
        melakukan retry dengan mekanisme backoff.
        
        Behavior:
            - Cek status kredensial (jika invalid, langsung return)
            - Connect ke broker dengan client.connect()
            - Start loop dengan client.loop_start()
            - Jika error: log error dan schedule reconnect dengan delay
              (jika reconnect enabled)
        """
        if self.status_auth == 'invalid_credentials':
            log_info("MQTT connection permanently stopped due to invalid credentials")
            return

        try:
            log_info(f"Connecting to MQTT broker {self.broker_url}:{self.broker_port}...")
            log_mqtt("CONNECTING", f"{self.broker_url}:{self.broker_port}", "Attempting to connect...")
            self.client.connect(self.broker_url, self.broker_port, self.keepalive)
            self.client.loop_start()
        except Exception as e:
            error_msg = str(e)
            log_error(f"Failed to start MQTT loop: {error_msg}")
            log_mqtt("ERROR", f"{self.broker_url}:{self.broker_port}", error_msg)

            # Reconnect hanya jika kredensial valid dan reconnect diaktifkan
            if self.status_auth != 'invalid_credentials' and self.reconnect_enabled:
                log_info(f"Retrying in {self.reconnect_delay} seconds...")
                threading.Timer(self.reconnect_delay, self._start_loop).start()
                self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)

    
    def subscribe(self, topic):
        """
        Subscribe ke topic MQTT.
        
        Method ini melakukan subscribe ke topic tertentu.
        Jika client belum connected, subscribe akan ditunda
        dan dicoba ulang saat reconnect.
        
        Args:
            topic (str): Nama topic yang akan disubscribe
            
        Behavior:
            - Cek apakah sudah subscribe (mencegah duplikasi)
            - Jika client connected: lakukan subscribe ke broker
            - Jika tidak connected: log warning dan simpan topic
              untuk dicoba ulang nanti
            - Tambahkan topic ke list subscribed_topics
        """
        
        if self.client and self.connected:
            self.client.subscribe(topic)
            log_success(f"Subscribed to topic: {topic}")
            log_mqtt("SUBSCRIBE", topic, "Subscription successful")
        else:
            log_warning(f"Cannot subscribe to {topic} - MQTT not connected, will retry on reconnect")
            log_mqtt("ERROR", topic, "Cannot subscribe - MQTT not connected")
        
    
    def publish(self, topic, payload, qos=0, retain=False):
        """
        Mempublish pesan ke MQTT broker.
        
        Method ini mengirim pesan ke topic yang ditentukan.
        
        Args:
            topic (str): Nama topic tujuan
            payload (any): Data yang akan dikirim. Jika bertipe dict,
                          akan dikonversi ke JSON string
            qos (int, optional): Quality of Service (0, 1, atau 2).
                                Defaults to 0.
            retain (bool, optional): Flag apakah pesan di-retain oleh broker.
                                    Defaults to False.
                                    
        Returns:
            bool: True jika publish berhasil, False jika gagal
            
        Behavior:
            - Cek status koneksi
            - Konversi payload ke string (JSON jika dict)
            - Publish ke broker
            - Log hasil publish
            - Return status keberhasilan
        """
        if self.client and self.connected:
            try:
                # Convert payload to string if it's dict
                if isinstance(payload, dict):
                    payload_str = json.dumps(payload)
                else:
                    payload_str = str(payload)
                
                # Log before publish
                log_mqtt("SEND", topic, payload_str)
                
                result = self.client.publish(topic, payload_str, qos=qos, retain=retain)
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    log_success(f"Published to {topic}")
                    return True
                else:
                    error_msg = f"Error code: {result.rc}"
                    log_error(f"Failed to publish to {topic}: {error_msg}")
                    log_mqtt("ERROR", topic, error_msg)
                    return False
            except Exception as e:
                error_msg = str(e)
                log_error(f"Error publishing message: {error_msg}")
                log_mqtt("ERROR", topic, error_msg)
                return False
        else:
            error_msg = "MQTT client not connected"
            log_warning(f"Cannot publish to {topic}: {error_msg}")
            log_mqtt("ERROR", topic, error_msg)
            return False
    
    def stop(self):
        """
        Menghentikan MQTT client.
        
        Method ini menghentikan loop MQTT dan memutuskan koneksi
        dengan broker secara clean.
        
        Behavior:
            - Stop loop dengan client.loop_stop()
            - Disconnect dari broker dengan client.disconnect()
            - Log status client dihentikan
        """
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            log_info("MQTT client stopped")
            log_mqtt("DISCONNECT", f"{self.broker_url}:{self.broker_port}", "Client stopped")

    
    def is_connected(self):
        """
        Memeriksa status koneksi MQTT client.
        
        Returns:
            bool: True jika client terhubung ke broker, False jika tidak
        """
        return self.connected


# Global instance
mqtt_client = MQTTClient()