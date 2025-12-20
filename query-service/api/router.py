from flask import Blueprint, request, jsonify
from datetime import datetime
from typing import Optional
from services.topic_service import get_topic_data
from utils.time_range import parse_time_range

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.route("/data/<sysname>/<topic>")
def get_topic_data_api(sysname: str, topic: str):
    try:
        start_time_str = request.args.get("start_time")
        end_time_str = request.args.get("end_time")
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        start_time, end_time = parse_time_range(
            request.args.get("start_time"),
            request.args.get("end_time"),
        )

        data = get_topic_data(
            sysname=sysname,
            topic=topic,
            page=page,
            per_page=per_page,
            start_time=start_time,
            end_time=end_time,
        )
        return jsonify(data)
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
