# app/db.py
import os
import ssl
from urllib.parse import urlparse, parse_qs
import psycopg2
from psycopg2.pool import SimpleConnectionPool

# Cargar .env de forma robusta
try:
    from dotenv import load_dotenv
    from pathlib import Path
    # primero raíz (junto a main.py), luego fallback a app/.env
    root_env = Path(__file__).resolve().parents[1] / ".env"
    app_env  = Path(__file__).resolve().parent / ".env"
    if root_env.exists():
        load_dotenv(root_env)
    elif app_env.exists():
        load_dotenv(app_env)
except Exception:
    # si no está python-dotenv no pasa nada; seguimos con variables del entorno
    pass

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL no definida. Crea un archivo .env en la RAÍZ con:\n"
        "DATABASE_URL=postgresql://...sslmode=require"
    )

# Parseo y parámetros
u = urlparse(DATABASE_URL)
USER = u.username
PWD  = u.password
HOST = u.hostname
PORT = u.port or 5432
DB   = (u.path or "/").lstrip("/")
qs   = parse_qs(u.query or "")

# SSL siempre activo para Neon
SSL_CTX = ssl.create_default_context()
SSL_MODE = (qs.get("sslmode", ["require"])[0]).lower()

def _new_conn():
    return psycopg2.connect(
        user=USER,
        password=PWD,
        host=HOST,
        port=PORT,
        dbname=DB,
        sslmode=SSL_MODE,
        sslrootcert=None,  # con 'require' no es necesario rootcert
    )

# Pool de conexiones
_pool: SimpleConnectionPool | None = None

def _pool_get():
    global _pool
    if _pool is None:
        _pool = SimpleConnectionPool(minconn=1, maxconn=5, dsn=None,
                                     user=USER, password=PWD,
                                     host=HOST, port=PORT, dbname=DB,
                                     sslmode=SSL_MODE)
    return _pool

def query_one(sql: str, params: tuple = ()):
    pool = _pool_get()
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            return row
    finally:
        pool.putconn(conn)

def execute(sql: str, params: tuple = ()):
    pool = _pool_get()
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
        conn.commit()
    finally:
        pool.putconn(conn)

def test_connection():
    row = query_one("SELECT 1;")
    print("Conexion OK" if row and row[0] == 1 else "Conexion FAIL")
