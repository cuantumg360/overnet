from fastapi import FastAPI, Form, Request, Header, HTTPException, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from app.router import route_task
from app.metrics import init_db, log_request, last_requests
from app.auth import create_user, auth_user, key_to_user
from app.db import get_conn

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
init_db()

# --- Auth middleware ---
def require_key(x_api_key: str = Header(None)):
    if not x_api_key:
        raise HTTPException(401, "missing x-api-key")
    user = key_to_user(x_api_key)
    if not user:
        raise HTTPException(401, "invalid key")
    return user

# --- Public pages ---
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/metrics")
def metrics():
    return JSONResponse(last_requests(20))

# --- Auth endpoints ---
@app.post("/signup")
def signup(email: str = Form(...), password: str = Form(...)):
    data = create_user(email, password)
    return {"ok": True, **data}

@app.post("/login")
def login(email: str = Form(...), password: str = Form(...)):
    data = auth_user(email, password)
    if not data:
        raise HTTPException(401, "bad credentials")
    return {"ok": True, **data}

@app.get("/me")
def me(user=Depends(require_key)):
    return {"ok": True, "user_id": str(user["id"]), "email": user["email"], "plan": user["plan"]}

# --- Protected inference ---
@app.post("/route")
def route(task: str = Form(...), text: str = Form(...), user=Depends(require_key)):
    result, meta = route_task(task, text)
    if meta:
        # log local sqlite (legacy)
        log_request(task, result.get("model"), meta["latency_ms"], meta["cost"], meta["tokens"])
        # log en Postgres
        try:
            con = get_conn(); cur = con.cursor()
            cur.execute("INSERT INTO usage(user_id,tokens,cost_cents,ok) VALUES(%s,%s,%s,%s)",
                        (user["id"], meta["tokens"], int(meta["cost"]*100), True))
            con.commit(); con.close()
        except Exception as e:
            print("usage log warn:", e)
    return JSONResponse(result)
