"""
Module      : apps.authentication.routes
Author      : Keyfin Suratman
Description : Blueprint untuk fitur autentikasi (login, register, logout)
"""

from flask import render_template, request, session, jsonify, url_for, redirect
from apps.authentication import blueprint
from apps.models import login_user, register_user


# ==========================
# ROUTE: Login
# ==========================
@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    """
    Menangani proses login user.

    Behavior:
        - Jika user sudah login (session['user_id'] ada), redirect otomatis ke dashboard
        - GET  -> Render halaman login jika belum login
        - POST -> Verifikasi credentials user dan buat session

    Request Form (POST):
        email    : str -> Email atau username user
        password : str -> Password user

    Response (JSON POST):
        success : bool
        message : str (jika gagal login)

    Session:
        session['user_id']
        session['username']
    """
    # ==========================
    # Cek user sudah login
    # ==========================
    if 'user_id' in session:
        return redirect(url_for('dashboard_blueprint.dashboard'))  # redirect ke dashboard

    if request.method == 'POST':
        username = request.form.get('email')
        password = request.form.get('password')

        success, result = login_user(username, password)

        if success:
            # Simpan informasi user di session
            session['user_id'] = result['id']
            session['username'] = result['username']

            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "message": result})

    # Render halaman login (GET request)
    return render_template('authentication/login.html')


# ==========================
# ROUTE: Register
# ==========================
@blueprint.route('/register', methods=['POST'])
def register():
    """
    Menangani pendaftaran user baru.

    Request Form (POST):
        email    : str -> Email user
        password : str -> Password user (minimal 6 karakter)

    Response (JSON):
        success : bool
        message : str
    """
    username = request.form.get('email')
    password = request.form.get('password')

    # Validasi input
    if not username or not password:
        return jsonify({"success": False, "message": "Email dan password harus diisi"})

    if len(password) < 6:
        return jsonify({"success": False, "message": "Password minimal 6 karakter"})

    # Panggil fungsi register dari model
    success, message = register_user(username, password)

    return jsonify({"success": success, "message": message})


# ==========================
# ROUTE: Logout
# ==========================
@blueprint.route('/logout')
def logout():
    """
    Logout user dan menghapus semua session.
    Redirect ke halaman login.
    """
    session.pop('user_id', None)
    session.pop('username', None)
    session.clear()

    return redirect(url_for('authentication_blueprint.login'))