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
    print("DB PATH:", db_path)  # Debug: tampilkan path database
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row  # agar hasil query bisa diakses seperti dict
    return conn


# ==========================
# REGISTER USER
# ==========================
def register_user(username: str, password: str):
    """
    Mendaftarkan user baru ke database.

    Args:
        username (str): Username / email user
        password (str): Password user (plain text)

    Returns:
        tuple(bool, str): 
            - True + message jika register berhasil
            - False + message jika gagal (misal username sudah ada)
    """
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Hash password sebelum disimpan
        hashed_password = generate_password_hash(password)

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_password)
        )
        conn.commit()
        return True, "Register berhasil"

    except sqlite3.IntegrityError:
        # Biasanya terjadi jika username sudah ada (UNIQUE constraint)
        return False, "Username sudah digunakan"

    except Exception as e:
        # Tangkap exception umum
        print("Error saat register user:", e)
        return False, f"Terjadi kesalahan Silakan Coba Lagi."

    finally:
        conn.close()


# ==========================
# LOGIN USER
# ==========================
def login_user(username: str, password: str):
    """
    Memverifikasi login user dengan username dan password.

    Args:
        username (str): Username / email user
        password (str): Password plain text

    Returns:
        tuple(bool, dict|str):
            - Jika berhasil login: (True, {"id": int, "username": str})
            - Jika gagal login: (False, "pesan error")
    """
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )
    user = cursor.fetchone()
    conn.close()

    if user:
        # Verifikasi password
        if check_password_hash(user["password"], password):
            return True, {
                "id": user["id"],
                "username": user["username"]
            }
        else:
            return False, "Password salah"
    else:
        return False, "User tidak ditemukan"