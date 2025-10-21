# app/__init__.py
from flask import Flask
from app.router import bp as router_bp
from app.auth import bp as auth_bp
from app.metrics import bp as metrics_bp

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    app.register_blueprint(router_bp)                 # /
    app.register_blueprint(auth_bp,   url_prefix="/auth")
    app.register_blueprint(metrics_bp, url_prefix="/metrics")

    return app

app = create_app()
