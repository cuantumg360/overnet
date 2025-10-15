import sqlite3, time, os
DB_PATH = "metrics.db"

def init_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("""
    CREATE TABLE IF NOT EXISTS requests(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      task TEXT, model TEXT,
      latency_ms INTEGER, cost REAL, tokens INTEGER, ts INTEGER
    )
    """)
    con.commit()
    con.close()

def log_request(task, model, latency_ms, cost, tokens):
    con = sqlite3.connect(DB_PATH)
    con.execute("INSERT INTO requests(task,model,latency_ms,cost,tokens,ts) VALUES(?,?,?,?,?,?)",
                (task, model, latency_ms, cost, tokens, int(time.time())))
    con.commit()
    con.close()

def last_requests(limit=20):
    con = sqlite3.connect(DB_PATH)
    cur = con.execute("SELECT task,model,latency_ms,cost,tokens,ts FROM requests ORDER BY id DESC LIMIT ?", (limit,))
    rows = [{"task":r[0],"model":r[1],"latency_ms":r[2],"cost":r[3],"tokens":r[4],"ts":r[5]} for r in cur.fetchall()]
    con.close()
    return rows
