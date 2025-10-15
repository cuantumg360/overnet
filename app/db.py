import os, psycopg2, psycopg2.extras

URL = os.getenv("DATABASE_URL")
if not URL:
    raise RuntimeError("DATABASE_URL no definida")

def get_conn():
    return psycopg2.connect(URL, cursor_factory=psycopg2.extras.RealDictCursor)
