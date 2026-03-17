"""
Flask Application Factory

File ini bertugas untuk:
1. Membuat instance aplikasi Flask
2. Memuat konfigurasi aplikasi
3. Mendaftarkan semua Blueprint (module aplikasi)

Struktur project yang diasumsikan:

apps/
 ├── authentication/
 │    └── routes.py
 │
 ├── dashboard/
 │    └── routes.py
 │
 ├── config.py
 │
 └── __init__.py  (file ini)
"""

import os
from flask import Flask
from importlib import import_module

def register_blueprints(app: Flask):
    """
    Mendaftarkan semua blueprint dari module aplikasi.

    Setiap module harus memiliki file:
        apps/<module>/routes.py

    Dan di dalamnya harus terdapat:
        blueprint = Blueprint(...)
    """

    modules = (
        "authentication",
        "dashboard"
    )

    for module_name in modules:
        module = import_module(f"apps.{module_name}.routes")
        app.register_blueprint(module.blueprint)



def create_app(config):
    """
    Application Factory.

    Parameter
    ---------
    config : object
        Class konfigurasi Flask yang akan digunakan
        (Debug / Production)

    Returns
    -------
    Flask
        Instance aplikasi Flask yang sudah siap digunakan.
    """

    # Contextual
    static_prefix = '/static'

    TEMPLATES_FOLDER = os.path.join(config.BASE_DIR, 'templates')
    STATIC_FOLDER = os.path.join(config.BASE_DIR, 'static')

    print(' > TEMPLATES_FOLDER: ' + TEMPLATES_FOLDER)
    print(' > STATIC_FOLDER:    ' + STATIC_FOLDER)

    app = Flask(
        __name__,
        static_url_path=static_prefix,
        template_folder=TEMPLATES_FOLDER,
        static_folder=STATIC_FOLDER
    )

    # Load konfigurasi
    app.config.from_object(config)

    # Register blueprint
    register_blueprints(app)

    return app