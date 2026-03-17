"""
Module      : apps.dashboard.routes
Author      : Keyfin Suratman
Description : Route untuk halaman dashboard dengan proteksi login
"""

from functools import wraps
from flask import render_template, session, redirect, url_for

from apps.dashboard import blueprint


# ==========================
# DECORATOR LOGIN REQUIRED
# ==========================
def login_required(f):
    """
    Decorator untuk memproteksi route agar hanya bisa diakses
    oleh user yang sudah login (session['user_id'] ada)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('authentication_blueprint.login'))
        return f(*args, **kwargs)
    return decorated_function


# ==========================
# ROUTE DASHBOARD
# ==========================
@blueprint.route('/')
@login_required
def dashboard():
    """
    Render halaman dashboard hanya untuk user yang sudah login.
    """
    return render_template('dashboard/dashboard.html', segment='dashboard')