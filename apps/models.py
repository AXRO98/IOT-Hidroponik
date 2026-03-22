"""
Module      : apps.models
Author      : Keyfin Suratman
Description : Fungsi model untuk autentikasi user (register & login)
"""

import sqlite3
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash


# ==========================
# CONNECT DATABASE
# ==========================
def connect_db():
    """
    Membuat koneksi ke database SQLite yang sudah dikonfigurasi di Flask.

    Returns:
        sqlite3.Connection: Objek koneksi database
    """
    db_path = current_app.config['DATABASE']
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn
