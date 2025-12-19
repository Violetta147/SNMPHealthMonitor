import time
from flask import request
from datetime import datetime
from typing import Optional
from utils.time_range import parse_time_range
from utils.logging import configure_logger

def register_socketio_events(socketio, ws_manager, get_topic_data):
    """
    Đăng ký tất cả Socket.IO event handlers cho query-service.

    socketio: Flask-SocketIO instance
    ws_manager: WebSocketManager instance
    get_topic_data: function để lấy dữ liệu metrics theo topic
    """
    logger = configure_logger(__name__)

    @socketio.on("connect")
    def handle_connect():
        sid = request.sid
        logger.info(f"Client connected, sid={sid}")

    @socketio.on("disconnect")
    def handle_disconnect():
        sid = request.sid
        logger.info(f"Client disconnected, sid={sid}")
        ws_manager.disconnect(sid)

    @socketio.on("subscribe")
    def handle_subscribe(data):
        """
        Client yêu cầu subscribe vào một sysname/topic.
        data: { 
            'sysname': str, 
            'topic': str
        }
        """
        sid = request.sid
        sysname = data.get("sysname")
        topic = data.get("topic") or "systemstatus"

        logger.info(f"Subscribe requested: sid={sid}, sysname={sysname}, topic={topic}")

        if not sysname:
            logger.warning(f"Missing sysname in subscribe payload: {data}")
            return

        # Đăng ký client vào topic
        ws_manager.connect(sid, sysname, topic)

        # Gửi dữ liệu ban đầu cho client vừa subscribe (Snapshot Mode - latest data)
        try:
            payload = get_topic_data(sysname, topic)
            socketio.emit(
                "data",
                {
                    "type": "data",
                    "topic": topic,
                    "sysname": sysname,
                    "data": payload,
                },
                to=sid,
            )
            logger.info(f"Sent initial {topic} data to sid={sid}")
        except Exception as e:
            logger.error(
                f"Error sending initial data for {sysname}/{topic} "
                f"to sid={sid}: {e}", exc_info=True
            )

    @socketio.on("ping")
    def handle_ping(data=None):
        """Đơn giản trả về pong để giữ kết nối."""
        sid = request.sid
        logger.debug(f"Ping from sid={sid}, data={data}")
        socketio.emit("pong", {"ts": time.time()}, to=sid)

    @socketio.on("paginate")
    def handle_paginate(data):
        """
        Xử lý pagination cho diskio (Snapshot Mode only):
        data: { 'sysname': str, 'topic': 'diskio', 'page': int, 'per_page': int }
        """
        sid = request.sid
        sysname = data.get("sysname")
        topic = data.get("topic", "diskio")
        page = int(data.get("page", 1))
        per_page = int(data.get("per_page", 10))

        logger.info(
            f"Paginate requested: sid={sid}, sysname={sysname}, "
            f"topic={topic}, page={page}, per_page={per_page}"
        )

        if not sysname:
            logger.warning(f"Missing sysname in paginate payload: {data}")
            return

        if topic != "diskio":
            logger.warning(f"Pagination only supported for diskio topic, got {topic}")
            return

        try:
            # Pagination only works in Snapshot Mode (no start_time)
            payload = get_topic_data(sysname, topic, page=page, per_page=per_page)
            socketio.emit(
                "data",
                {
                    "type": "data",
                    "topic": topic,
                    "sysname": sysname,
                    "data": payload,
                },
                to=sid,
            )
            logger.info(f"Sent paginated {topic} data to sid={sid}")
        except Exception as e:
            logger.error(
                f"Error sending paginated data for {sysname}/{topic} "
                f"to sid={sid}: {e}", exc_info=True
            )

    @socketio.on("query_range")
    def handle_query_range(data):
        """
        Client yêu cầu historical data trong một khoảng thời gian (Range Mode).
        data: {
            'sysname': str,
            'topic': str,
            'start_time': str (ISO format datetime),
            'end_time': str (ISO format datetime, optional, defaults to now),
            'page': int (optional, for diskio only),
            'per_page': int (optional, for diskio only)
        }
        """
        sid = request.sid
        sysname = data.get("sysname")
        topic = data.get("topic", "systemstatus")
        start_time_str = data.get("start_time")
        end_time_str = data.get("end_time")
        page = int(data.get("page", 1))
        per_page = int(data.get("per_page", 10))

        logger.info(
            f"Query range requested: sid={sid}, sysname={sysname}, topic={topic}, "
            f"start_time={start_time_str}, end_time={end_time_str}"
        )

        if not sysname:
            logger.error(f"Missing sysname in query_range payload: {data}")
            socketio.emit("error", {"message": "Missing sysname"}, to=sid)
            return

        if not start_time_str:
            logger.error(f"Missing start_time in query_range payload: {data}")
            socketio.emit("error", {"message": "Missing start_time for range query"}, to=sid)
            return

        try:
            # Parse datetime strings
            start_time, end_time = parse_time_range(start_time_str, end_time_str)

            # Fetch historical data (Range Mode)
            payload = get_topic_data(
                sysname=sysname,
                topic=topic,
                start_time=start_time,
                end_time=end_time,
                page=page,
                per_page=per_page,
                # Range Mode with automatic downsampling
            )

            socketio.emit(
                "data",
                {
                    "type": "data",
                    "topic": topic,
                    "sysname": sysname,
                    "data": payload,
                    "range": {
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat(),
                    },
                },
                to=sid,
            )
            logger.info(f"Sent range query {topic} data to sid={sid}")
        except ValueError as e:
            error_msg = f"Invalid datetime format: {e}"
            logger.error(error_msg)
            socketio.emit("error", {"message": error_msg}, to=sid)
        except Exception as e:
            logger.error(
                f"Error sending range query data for {sysname}/{topic} to sid={sid}: {e}",
                exc_info=True
            )
            socketio.emit("error", {"message": str(e)}, to=sid)
