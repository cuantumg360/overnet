import os
import psycopg2
from psycopg2.pool import SimpleConnectionPool

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL no definida")

_pool = SimpleConnectionPool(minconn=1, maxconn=5, dsn=DATABASE_URL)

def get_conn():
    return _pool.getconn()

def put_conn(conn):
    if conn:
        _pool.putconn(conn)

def close_pool():
    if _pool:
        _pool.closeall()

def execute(sql: str, params: tuple | None = None):
    conn = get_conn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(sql, params or ())
    finally:
        put_conn(conn)

def query_one(sql: str, params: tuple | None = None):
    conn = get_conn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchone()
    finally:
        put_conn(conn)
