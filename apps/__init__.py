"""
Flask Application Factory
"""

import os
from flask import Flask, redirect
from importlib import import_module

from apps.extensions import login_manager, socketio

# -------------------------------------------------
# CONFIG
# -------------------------------------------------

BLUEPRINT_MODULES = [
    "authentication",
    "dashboard",
]

# -------------------------------------------------
# BLUEPRINT REGISTRATION
# -------------------------------------------------

def register_blueprints(app: Flask):
    for module_name in BLUEPRINT_MODULES:
        module = import_module(f"apps.{module_name}.routes")
        app.register_blueprint(module.blueprint)

# -------------------------------------------------
# EXTENSIONS
# -------------------------------------------------

def register_extensions(app: Flask):
    login_manager.init_app(app)
    socketio.init_app(app)

    login_manager.login_view = "authentication_blueprint.login"

# -------------------------------------------------
# HANDLERS
# -------------------------------------------------

def register_handlers(app: Flask):

    @login_manager.unauthorized_handler
    def unauthorized():
        return redirect("/login")

# -------------------------------------------------
# APP FACTORY
# -------------------------------------------------

def create_app(config):
    """Create Flask App (Factory Pattern)"""

    base_dir = config.BASE_DIR

    app = Flask(
        __name__,
        static_url_path="/static",
        template_folder=os.path.join(base_dir, "templates"),
        static_folder=os.path.join(base_dir, "static"),
    )

    # Load config
    app.config.from_object(config)

    # Register core components
    register_extensions(app)
    register_blueprints(app)
    register_handlers(app)

    return app