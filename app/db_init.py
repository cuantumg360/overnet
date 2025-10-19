import os, psycopg2

url = os.getenv("DATABASE_URL")
assert url, "DATABASE_URL no definida"

con = psycopg2.connect(url)
cur = con.cursor()

# UUIDs
cur.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS api_keys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  key TEXT UNIQUE NOT NULL,
  active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW()
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS usage (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  ts TIMESTAMP DEFAULT NOW(),
  tokens INTEGER,
  cost_cents INTEGER,
  ok BOOLEAN
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS plans (
  user_id UUID PRIMARY KEY REFERENCES users(id),
  plan TEXT DEFAULT 'free',
  renew_at TIMESTAMP DEFAULT NOW() + interval '30 days'
);
""")

con.commit()
con.close()
print("OK: tablas creadas")
