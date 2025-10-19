# app/auth.py
from flask import Blueprint, request, jsonify
from functools import wraps
import secrets
from .db import query_one, execute

bp = Blueprint("auth", __name__)

# --------- helper: hash de contraseña muy simple (demo) ----------
import hashlib
def generate_password_hash(pwd: str) -> str:
    return hashlib.sha256(pwd.encode("utf-8")).hexdigest()

def check_password_hash(pwd_hash: str, pwd: str) -> bool:
    return pwd_hash == generate_password_hash(pwd)

# --------- decorador que EXIGE API key activa ----------
def require_api_key(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return jsonify(ok=False, error="Falta X-API-Key"), 401
        row = query_one(
            "SELECT user_id FROM api_keys WHERE key=%s AND active=TRUE LIMIT 1",
            (api_key,),
        )
        if not row:
            return jsonify(ok=False, error="API key inválida"), 401
        return fn(*args, **kwargs)
    return wrapper

# --------- endpoints de auth ----------
@bp.post("/signup")
def signup():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify(ok=False, error="Email y contraseña son requeridos"), 400

    row = query_one("SELECT id FROM users WHERE email=%s LIMIT 1", (email,))
    if row:
        return jsonify(ok=False, error="Email ya registrado"), 409

    pwd_hash = generate_password_hash(password)
    new_id = execute(
        "INSERT INTO users(email, password_hash) VALUES(%s,%s) RETURNING id",
        (email, pwd_hash),
        fetch="one",
    )[0]

    api_key = secrets.token_urlsafe(32)
    execute(
        "INSERT INTO api_keys(user_id, key, active) VALUES(%s,%s,TRUE)",
        (new_id, api_key),
    )
    return jsonify(ok=True, user_id=new_id, api_key=api_key), 201

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
    if not check_password_hash(pwd_hash, password):
        return jsonify(ok=False, error="Contraseña incorrecta"), 401

    # reutiliza o crea una API key activa
    k = query_one("SELECT key FROM api_keys WHERE user_id=%s AND active=TRUE LIMIT 1", (user_id,))
    if k:
        api_key = k[0]
    else:
        api_key = secrets.token_urlsafe(32)
        execute("INSERT INTO api_keys(user_id, key, active) VALUES(%s,%s,TRUE)", (user_id, api_key))

    return jsonify(ok=True, user_id=user_id, api_key=api_key), 200
