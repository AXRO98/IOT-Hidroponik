"""
File        : run.py
Author      : Keyfin Agustio Suratman
Description : App dashboard untuk IoT Hidroponik project robotik SMA Negeri 7 Manado.
Created     : 2026-03-16
"""

import os
import datetime
from sys import exit

from dotenv import load_dotenv
from flask_minify import Minify
from flask import request

from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman

from apps.config import config_dict
from apps import create_app


# -------------------------------------------------
# Load environment variables
# -------------------------------------------------

load_dotenv()


# -------------------------------------------------
# Debug Mode
# -------------------------------------------------

DEBUG = (os.getenv("DEBUG", "False") == "True")
PORT = int(os.getenv("PORT", 5000))


# -------------------------------------------------
# Load Configuration
# -------------------------------------------------

config_mode = "Debug" if DEBUG else "Production"

try:
    app_config = config_dict[config_mode]

except KeyError:
    exit("Error: Invalid <config_mode>. Expected values [Debug, Production]")


# -------------------------------------------------
# Create Flask App
# -------------------------------------------------

app = create_app(app_config)


# -------------------------------------------------
# Access Logging
# -------------------------------------------------

LOG_FILE = "log.txt"

def write_log(ip, method, path, status, device):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_line = f"[{timestamp}] [{ip}] {method} {path} | {status} | Device: {device}\n"

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line)


# -------------------------------------------------
# Enable HTML Minification
# -------------------------------------------------

if not DEBUG:
    Minify(app=app, html=True, js=True, cssless=True)
    print(" [INFO] Minify: ON")

    # -------------------------------------------------
    # Security: CSRF Protection
    # -------------------------------------------------

    csrf = CSRFProtect(app)
    print(" [INFO] CSRF Protection: ON")


    # -------------------------------------------------
    # Security: Secure Headers
    # -------------------------------------------------

    #Talisman(app)
    print(" [INFO] Secure Headers: ON")
    

    # -------------------------------------------------
    # Access Logging: Log each request to console
    # -------------------------------------------------

    @app.after_request
    def log_request(response):

        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        method = request.method
        path = request.path
        status = response.status_code
        device = request.headers.get("User-Agent", "Unknown Device")

        # Jika static dan status 304 → abaikan
        if path.startswith("/static/") and status == 304:
            return response

        write_log(ip, method, path, status, device)

        return response


# -------------------------------------------------
# Debug Logging
# -------------------------------------------------

if DEBUG:
    app.logger.info(f"DEBUG = {DEBUG}")
    app.logger.info(f"PORT  = {PORT}")


# -------------------------------------------------
# Run Server
# -------------------------------------------------

if __name__ == "__main__":

    try:
        app.run(
            debug=DEBUG,
            host="0.0.0.0",
            port=PORT
        )

    except Exception as error_page:

        print("[=========================[ ERROR ]=========================]")
        print(f"Error: {error_page}")
        print("[===========================================================]")