from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from app.router import route_task
from app.metrics import init_db, log_request, last_requests

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

init_db()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/route")
def route(task: str = Form(...), text: str = Form(...)):
    result, meta = route_task(task, text)
    if meta:
        log_request(task, result.get("model"), meta["latency_ms"], meta["cost"], meta["tokens"])
    return JSONResponse(result)

@app.get("/metrics")
def metrics():
    return JSONResponse(last_requests(20))
