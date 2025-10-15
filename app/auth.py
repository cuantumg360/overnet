import secrets
from passlib.hash import bcrypt
from app.db import get_conn

def hash_pw(pw:str)->str:
    return bcrypt.hash(pw)

def verify_pw(pw:str, h:str)->bool:
    return bcrypt.verify(pw, h)

def new_api_key()->str:
    return secrets.token_urlsafe(32)

def create_user(email:str, password:str):
    with get_conn() as con, con.cursor() as cur:
        cur.execute("INSERT INTO users(email,password_hash) VALUES(%s,%s) RETURNING id",
                    (email, hash_pw(password)))
        uid = cur.fetchone()["id"]
        key = new_api_key()
        cur.execute("INSERT INTO api_keys(user_id,key) VALUES(%s,%s)", (uid, key))
        cur.execute("INSERT INTO plans(user_id,plan) VALUES(%s,'free') ON CONFLICT (user_id) DO NOTHING", (uid,))
    return {"user_id": str(uid), "api_key": key}

def auth_user(email:str, password:str):
    with get_conn() as con, con.cursor() as cur:
        cur.execute("SELECT id,password_hash FROM users WHERE email=%s", (email,))
        row = cur.fetchone()
        if not row or not verify_pw(password, row["password_hash"]):
            return None
        uid = row["id"]
        cur.execute("SELECT key,active FROM api_keys WHERE user_id=%s ORDER BY created_at DESC LIMIT 1", (uid,))
        k = cur.fetchone()
    return {"user_id": str(uid), "api_key": k["key"], "active": k["active"]}

def key_to_user(api_key:str):
    with get_conn() as con, con.cursor() as cur:
        cur.execute("""
            SELECT u.id,u.email,COALESCE(p.plan,'free') AS plan
            FROM api_keys k
            JOIN users u ON u.id=k.user_id
            LEFT JOIN plans p ON p.user_id=u.id
            WHERE k.key=%s AND k.active=TRUE
        """, (api_key,))
        return cur.fetchone()
