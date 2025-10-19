from flask import Flask, jsonify, render_template
from flask_cors import CORS
from .db import execute
from .auth import bp as auth_bp
from .api import bp as api_bp

SCHEMA_SQL = """
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS api_keys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  key TEXT UNIQUE NOT NULL,
  active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW()
);
"""

def create_app():
    app = Flask(__name__)
    CORS(app)

    # init DB idempotente
    execute(SCHEMA_SQL)

    @app.get("/")
    def landing():
        return render_template("index.html")

    @app.get("/health")
    def health():
        return jsonify(ok=True), 200

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(api_bp)  # /echo

    return app
