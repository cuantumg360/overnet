import os, ssl
from urllib.parse import urlparse, unquote
import pg8000
from queue import Queue, Empty

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL no definida")

# parsea la URL de Postgres (Neon)
u = urlparse(DATABASE_URL)
DB_KW = {
    "host": u.hostname,
    "port": u.port or 5432,
    "database": u.path.lstrip("/"),
    "user": unquote(u.username or ""),
    "password": unquote(u.password or ""),
    "ssl_context": ssl.create_default_context(),
}

# pool simple
_MIN, _MAX = 1, 5
_pool = Queue(maxsize=_MAX)
_curr = 0

def _new_conn():
    return pg8000.connect(**DB_KW)

def get_conn():
    global _curr
    try:
        return _pool.get_nowait()
    except Empty:
        if _curr < _MAX:
            _curr += 1
            return _new_conn()
        # espera a que liberen
        return _pool.get()

def put_conn(conn):
    try:
        _pool.put_nowait(conn)
    except:
        try:
            conn.close()
        except:
            pass

def close_pool():
    while True:
        try:
            c = _pool.get_nowait()
            c.close()
        except Empty:
            break

def execute(sql: str, params: tuple | None = None):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        conn.commit()
        cur.close()
    finally:
        put_conn(conn)

def query_one(sql: str, params: tuple | None = None):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        row = cur.fetchone()
        cur.close()
        return row
    finally:
        put_conn(conn)
