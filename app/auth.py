from flask import Blueprint, request, jsonify
import bcrypt, secrets
from .db import query_one, execute

bp = Blueprint("auth", __name__)

def require_api_key(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        key = request.headers.get("X-API-Key")
        if not key:
            return jsonify(ok=False, error="API key requerida"), 401
        row = query_one("SELECT user_id FROM api_keys WHERE key=%s AND active=TRUE LIMIT 1", (key,))
        if not row:
            return jsonify(ok=False, error="API key inválida"), 401
        return f(*args, **kwargs)
    return wrapper

def _hash(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def _check(pw: str, hashed: str) -> bool:
    return bcrypt.checkpw(pw.encode(), hashed.encode())

@bp.post("/signup")
def signup():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify(ok=False, error="Email y contraseña son requeridos"), 400

    if query_one("SELECT 1 FROM users WHERE email=%s LIMIT 1", (email,)):
        return jsonify(ok=False, error="Email ya registrado"), 409

    pwd_hash = _hash(password)
    execute("INSERT INTO users(email, password_hash) VALUES (%s, %s)", (email, pwd_hash))

    api_key = secrets.token_urlsafe(32)
    execute("""
        INSERT INTO api_keys(user_id, key, active)
        VALUES ((SELECT id FROM users WHERE email=%s LIMIT 1), %s, TRUE)
    """, (email, api_key))

    user_id = query_one("SELECT id FROM users WHERE email=%s", (email,))[0]
    return jsonify(ok=True, api_key=api_key, user_id=str(user_id)), 201

@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify(ok=False, error="Email y contraseña son requeridos"), 400

    row = query_one("SELECT id, password_hash FROM users WHERE email=%s LIMIT 1", (email,))
    if not row:
        return jsonify(ok=False, error="Credenciales inválidas"), 401

    user_id, pwd_hash = row
    if not _check(password, pwd_hash):
        return jsonify(ok=False, error="Credenciales inválidas"), 401

    k = query_one("SELECT key FROM api_keys WHERE user_id=%s AND active=TRUE LIMIT 1", (user_id,))
    api_key = k[0] if k else None
    if not api_key:
        api_key = secrets.token_urlsafe(32)
        execute("INSERT INTO api_keys(user_id, key, active) VALUES (%s, %s, TRUE)", (user_id, api_key))

    return jsonify(ok=True, user_id=str(user_id), api_key=api_key), 200
