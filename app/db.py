# app/db.py
import os
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager

# -----------------------------------------------------------------------------
# Configuración de conexión
# -----------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL no definida en variables de entorno")

# Crea un pool de conexiones seguro y reutilizable
db_pool = psycopg2.pool.SimpleConnectionPool(
    1,                      # conexiones mínimas
    10,                     # conexiones máximas
    DATABASE_URL,
    sslmode="require"
)

# -----------------------------------------------------------------------------
# Helpers de conexión y ejecución
# -----------------------------------------------------------------------------
@contextmanager
def get_conn():
    """Devuelve una conexión del pool."""
    conn = db_pool.getconn()
    try:
        yield conn
    finally:
        db_pool.putconn(conn)

@contextmanager
def get_cursor():
    """Devuelve un cursor y maneja commit automáticamente."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            yield cur
            conn.commit()

# -----------------------------------------------------------------------------
# Funciones simples de consulta
# -----------------------------------------------------------------------------
def query_one(sql, params=()):
    """Ejecuta SELECT y devuelve una sola fila o None."""
    with get_cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone()

def query_all(sql, params=()):
    """Ejecuta SELECT y devuelve todas las filas."""
    with get_cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()

def execute(sql, params=()):
    """Ejecuta INSERT/UPDATE/DELETE y devuelve número de filas afectadas."""
    with get_cursor() as cur:
        cur.execute(sql, params)
        return cur.rowcount

# -----------------------------------------------------------------------------
# Prueba rápida de conexión (para health check)
# -----------------------------------------------------------------------------
def test_connection():
    try:
        with get_cursor() as cur:
            cur.execute("SELECT 1;")
            return True
    except Exception as e:
        print(f"Error de conexión: {e}")
        return False
