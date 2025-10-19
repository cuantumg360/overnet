# app/db.py
import os
from contextlib import contextmanager
import psycopg  # psycopg 3

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL no definida")

# --- helpers de conexión -----------------------------------------------

@contextmanager
def _conn():
    # autocommit para no gestionar commits manuales en utilidades simples
    with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
        yield conn

@contextmanager
def _cursor():
    with _conn() as conn:
        with conn.cursor() as cur:
            yield cur

# --- API mínima que usa el resto de módulos -----------------------------

def query_one(sql, params=()):
    """Devuelve una sola fila o None."""
    with _cursor() as cur:
        cur.execute(sql, params)
        row = cur.fetchone()
        return row

def execute(sql, params=()):
    """Ejecuta INSERT/UPDATE/DELETE. Devuelve filas afectadas si aplica."""
    with _cursor() as cur:
        cur.execute(sql, params)
        # en autocommit no hace falta commit; rowcount disponible
        return cur.rowcount

# útil para probar en consola/render
def test_connection():
    try:
        with _cursor() as cur:
            cur.execute("SELECT 1")
            return True
    except psycopg.Error:
        return False
