# app/route.py
from flask import Blueprint, render_template

bp = Blueprint("ui", __name__)

@bp.get("/")
def home():
    # renderiza templates/landing.html
    return render_template("landing.html")
