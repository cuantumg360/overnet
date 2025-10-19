import os
import psycopg2

try:
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
    tablas = [r[0] for r in cur.fetchall()]
    print("Tablas en la base de datos:", tablas)
    cur.close()
    conn.close()
except Exception as e:
    print("Error:", e)
