# app/db.py
import os
import psycopg2
from dotenv import load_dotenv

# 1. Cargar .env (busca en raíz del proyecto y en /app)
load_dotenv()
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"), override=False)

# 2. Obtener DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL no definida")

# 3. Configuración de conexión segura
CONNECT_KW = dict(
    sslmode="require",
    keepalives=1,
    keepalives_idle=30,
    keepalives_interval=10,
    keepalives_count=5,
    connect_timeout=10,
)

# 4. Función interna para abrir conexión
def _conn():
    return psycopg2.connect(DATABASE_URL, **CONNECT_KW)

# 5. Query que devuelve un solo resultado
def query_one(sql, params=()):
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone()

# 6. Ejecutar (insert/update/delete) o devolver resultados
def execute(sql, params=(), fetch=None):
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            if fetch == "one":
                return cur.fetchone()
            if fetch == "all":
                return cur.fetchall()
            return None

# 7. Probar conexión
def test_connection():
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            print("✅ Conexion OK")
