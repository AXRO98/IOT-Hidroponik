"""
Module      : apps.dashboard.routes
Author      : Keyfin Suratman
Description : Route untuk halaman dashboard dengan proteksi login
"""

from flask import render_template
from flask_login import login_required, current_user

from apps.dashboard import blueprint


# ==========================
# ROUTE DASHBOARD
# ==========================
@blueprint.route('/')
@login_required  
def dashboard():
    """
    Render halaman dashboard hanya untuk user yang sudah login.
    """
    # current_user otomatis tersedia dari Flask-Login
    return render_template('dashboard/dashboard.html', 
                         segment='dashboard',
                         user=current_user)  # Kirim user ke template jika perlu