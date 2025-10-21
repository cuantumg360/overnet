# app/router.py
from flask import Blueprint, render_template, jsonify, request

bp = Blueprint("router", __name__)

@bp.get("/")
def landing():
    # Renderiza la landing
    return render_template("index.html")

@bp.get("/health")
def health():
    return jsonify(ok=True, status="ok")
