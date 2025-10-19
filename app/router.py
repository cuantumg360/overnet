# app/router.py
from flask import Blueprint, request, jsonify, g
from .db import get_conn, put_conn
import bcrypt
import uuid

bp = Blueprint("api", __name__)

# --------- helpers ----------
def _get_user_by_email(cur, email):
    cur.execute("SELECT id, password_hash FROM users WHERE email=%s", (email,))
    return cur.fetchone()

def _issue_api_key(cur, user_id):
    # desactiva claves previas y crea una nueva
    cur.execute("UPDATE api_keys SET active=FALSE WHERE user_id=%s", (user_id,))
    api_key = uuid.uuid4().hex
    cur.execute(
        "INSERT INTO api_keys (user_id, key, active) VALUES (%s, %s, TRUE) RETURNING key",
        (user_id, api_key),
    )
    return cur.fetchone()[0]

def require_key():
    key = request.headers.get("X-API-Key")
    if not key:
        return None
    conn = get_conn(); cur = conn.cursor()
    try:
        cur.execute(
            "SELECT u.id, u.email FROM api_keys k JOIN users u ON u.id=k.user_id "
            "WHERE k.key=%s AND k.active=TRUE",
            (key,),
        )
        row = cur.fetchone()
        return (conn, cur, row)  # quien llame debe cerrar
    except Exception:
        put_conn(conn); return None

# --------- rutas ----------
@bp.post("/signup")
def signup():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or not password:
        return jsonify(ok=False, error="email y password requeridos"), 400

    conn = get_conn(); cur = conn.cursor()
    try:
        if _get_user_by_email(cur, email):
            put_conn(conn)
            return jsonify(ok=False, error="usuario ya existe"), 409

        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        cur.execute(
            "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id",
            (email, pw_hash),
        )
        user_id = cur.fetchone()[0]
        api_key = _issue_api_key(cur, user_id)
        conn.commit()
        return jsonify(ok=True, user_id=str(user_id), api_key=api_key), 201
    except Exception as e:
        conn.rollback()
        return jsonify(ok=False, error=str(e)), 500
    finally:
        put_conn(conn)

@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or not password:
        return jsonify(ok=False, error="email y password requeridos"), 400

    conn = get_conn(); cur = conn.cursor()
    try:
        row = _get_user_by_email(cur, email)
        if not row:
            return jsonify(ok=False, error="credenciales inválidas"), 401
        user_id, pw_hash = row
        if not bcrypt.checkpw(password.encode(), pw_hash.encode()):
            return jsonify(ok=False, error="credenciales inválidas"), 401

        api_key = _issue_api_key(cur, user_id)
        conn.commit()
        return jsonify(ok=True, user_id=str(user_id), api_key=api_key), 200
    except Exception as e:
        conn.rollback()
        return jsonify(ok=False, error=str(e)), 500
    finally:
        put_conn(conn)

@bp.get("/me")
def me():
    auth = require_key()
    if not auth:
        return jsonify(ok=False, error="X-API-Key requerida"), 401
    conn, cur, row = auth
    try:
        if not row:
            return jsonify(ok=False, error="clave inválida"), 401
        user_id, email = row
        return jsonify(ok=True, user={"id": str(user_id), "email": email})
    finally:
        cur.close(); put_conn(conn)

@bp.post("/logs")
def add_log():
    auth = require_key()
    if not auth:
        return jsonify(ok=False, error="X-API-Key requerida"), 401
    conn, cur, row = auth
    try:
        user_id, _ = row
        data = request.get_json(silent=True) or {}
        route = data.get("route") or "/unknown"
        level = data.get("level") or "info"
        message = data.get("message") or ""
        # crea route si no existe
        cur.execute(
            "INSERT INTO routes (path) VALUES (%s) ON CONFLICT (path) DO NOTHING RETURNING id",
            (route,),
        )
        if cur.rowcount:
            route_id = cur.fetchone()[0]
        else:
            cur.execute("SELECT id FROM routes WHERE path=%s", (route,))
            route_id = cur.fetchone()[0]
        # log
        cur.execute(
            "INSERT INTO logs (route_id, level, message) VALUES (%s, %s, %s)",
            (route_id, level, message),
        )
        conn.commit()
        return jsonify(ok=True), 201
    except Exception as e:
        conn.rollback()
        return jsonify(ok=False, error=str(e)), 500
    finally:
        put_conn(conn)

@bp.get("/logs")
def list_logs():
    auth = require_key()
    if not auth:
        return jsonify(ok=False, error="X-API-Key requerida"), 401
    conn, cur, _ = auth
    try:
        cur.execute(
            "SELECT l.id, r.path, l.level, l.message, l.created_at "
            "FROM logs l JOIN routes r ON r.id=l.route_id "
            "ORDER BY l.created_at DESC LIMIT 50"
        )
        rows = cur.fetchall()
        out = [
            {"id": str(r[0]), "route": r[1], "level": r[2], "message": r[3], "created_at": r[4].isoformat()}
            for r in rows
        ]
        return jsonify(ok=True, logs=out)
    finally:
        put_conn(conn)
