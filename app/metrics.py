# app/metrics.py
from flask import Blueprint, jsonify

bp = Blueprint("metrics", __name__, url_prefix="/metrics")

@bp.get("/")
def get_metrics():
    data = {"users": 42, "requests_today": 123, "uptime_hours": 12.5}
    return jsonify(data)
