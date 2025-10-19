# app/__init__.py
from flask import Flask, jsonify, render_template
from dotenv import load_dotenv
from flask_cors import CORS  # seguro para futuro, aquí no es crítico

def create_app():
    load_dotenv()
    app = Flask(__name__, template_folder="../templates")
    CORS(app, resources={r"/*": {"origins": "*"}})

    @app.get("/")
    def root():
        return render_template("index.html")

    @app.get("/health")
    def health():
        return jsonify(ok=True), 200

    # blueprints existentes
    from .auth import bp as auth_bp
    from .api import bp as api_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(api_bp)  # /echo

    return app
