from flask import Blueprint, request, jsonify
from .auth import require_api_key

bp = Blueprint("api", __name__)

@bp.post("/echo")
@require_api_key
def echo():
    data = request.get_json(silent=True) or {}
    return jsonify(ok=True, msg=data.get("msg", "hola")), 200
