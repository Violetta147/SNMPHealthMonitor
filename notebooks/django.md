asgiref (ASGI Reference Library)
Django có khả năng chạy trên WSGI (đồng bộ, blocking)
Muốn chạy Websocket, Async Views (xử lý nhiều reqquests cùng lúc mà không cần nhiều luồng) cần chuyển sang ASGI

sqlparse là thư viện phân tích và format câu lệnh SQL
pretty-print và phân tích cú pháp sql nhưng không thực thi hay kiểm tra lỗi logic của câu lệnh

python manage.py sqlmigrate, sử dụng chế độ debug để xem các query đang chạy

Django Ninja hiện đại hơn, nhanh hơn (async, Pydantic), code gọn gàng, tự động tạo docs, lý tưởng cho API hiệu năng cao, microservices.

Chọn DRF nếu:
Dự án lớn, cần nhiều tính năng phức tạp, authentication/authorization đa dạng.
Bạn đã quen thuộc với mô hình Class-Based Views (CBVs) của Django.
Cần hệ sinh thái lớn, nhiều tài liệu, và đã có kinh nghiệm.
Chọn Ninja nếu:
Ưu tiên tốc độ, hiệu năng cao, hỗ trợ async/await.
Muốn code ngắn gọn, sử dụng Pydantic (validation dữ liệu), tự động tạo tài liệu API (Swagger/OpenAPI).
Làm microservices hoặc API đơn giản, cần phát triển nhanh.

# Django Refactoring Plan

## 1. Solution Architecture & Comparison

### Current Architecture Assessment
- **Structure:** Hybrid "Direct Write + UDP Notify" model.
    - **Collector (`raspberrypi`):** Fetches SNMP data, writes **directly** to MySQL, and sends UDP packet to `query-service`.
    - **Backend (`query-service`):** Flask App that listens on UDP for real-time trigger (then streams via Socket.IO) and reads from MySQL for history/fallback.
- **Limitations:**
    - **Tight Coupling:** The Collector acts as a "DB Writer", requiring direct DB access (security risk for remote agents).
    - **Race Conditions:** `query-service` might try to read data before the transaction commits in `raspberrypi` (though UDP usually arrives after).
    - **Complexity:** Dual data paths (UDP path vs DB path).

### Proposed Django Architecture (ASGI + Channels)
We will move to a **Receiver-Processor** pattern using **Django Channels** and **ASGI**.

**Components:**
1.  **Frontend:** Connects via WebSocket to `ws://server/ws/metrics/`.
2.  **Django Backend (ASGI):**
    -   **API Layer (Django Ninja):** For metadata, configuration, and historical queries (REST).
    -   **Real-time Layer (Django Channels):** Handles WebSockets.
3.  **Data Ingestion (The biggest change):**
    -   **Option A (Modern & Robust):** **Agent pushes via HTTP/2 (Django Ninja)**. The Agent collects data -> POSTs to Django -> Django writes to DB (MySQL) -> Django signals Channel layer.
    -   **Option B (High Throughput/Current approach):** **UDP Worker**. A custom Django Management Command runs an Async UDP Server.
        -   Receives Packet -> 1. Saves to DB (async) -> 2. Sends to Channel Group `metrics_<sysname>`.

**Recommendation:** Go with **Option A (HTTP Push via Django Ninja)** for simplicity and reliability, or **Option B** if packet volume is massive (>1000/sec). Given this is a monitoring dashboard, HTTP/2 (via Django Ninja Async) is efficient enough and drastically simplifies architecture (Agent doesn't need DB driver).

### Architecture Diagram
`Agent` --(HTTP/JSON)--> `Django (Ninja View)` --(save)--> `MySQL`
                                     |
                                     +--(Group Send)--> `Channels` --(WS)--> `Frontend`

---

## 2. Code Organization (Structure)

Recommended Django Project Layout "Config-driven":

```text
dashboard_project/
├── manage.py
├── pyproject.toml              # Dependency management (Poetry/UV recommended)
├── config/                     # Replacement for standard 'project_name' folder
│   ├── __init__.py
│   ├── asgi.py                # ASGI Entry point
│   ├── settings.py            # Unified settings
│   ├── urls.py
│   └── wsgi.py
├── apps/                       # Dedicated folder for Apps
│   ├── core/                  # Common utils, base models
│   ├── devices/               # Device management (SNMP configs, Sysinfo)
│   ├── metrics/               # The heavy lifter: Metric models
│   │   ├── migrations/
│   │   ├── models.py          # Metric, Measurement
│   │   └── api.py             # Ingestion API (Django Ninja)
│   └── realtime/              # WebSocket logic
│       ├── consumers.py       # AsyncJsonWebsocketConsumer
│       └── routing.py
└── infra/                     # Docker, Nginx, Systemd configs
```

### Layer Separation
1.  **Service Layer (`services.py` in apps):**
    -   Encapsulate SNMP logic here (moving from `raspberrypi`).
    -   Example: `SnmpService.fetch_metrics(host, community)`.
2.  **Data Access Layer (Models + Managers):**
    -   Use standard Django Managers or custom SQL for time-series bucketing.
3.  **API Layer (Django Ninja):**
    -   Define Schema (Pydantic) -> View Function -> Call Service/Model -> Return Schema.

---

## 3. Detailed Tech Stack Recommendation

### Core: Django 5.0+ with Django Ninja
-   **Django 5.x:** Native Async support is mature.
-   **API Framework: Django Ninja.**
    -   *Why?* It uses **Pydantic** directly (faster than DRF Serializers). It supports **Async views** natively (`async def api(...)`), which is crucial for handling high-concurrency ingestion without blocking threads. DRF's async support is still evolving/partial.

### Async/Task Stack: Redis Queue (RQ) or Just Native Async
-   **Recommendation:** Start with **Just Native Async** + **Django Background Tasks** or **RQ**.
-   *Why?* Celery is overkill and complex (requires RabbitMQ usually for reliability). If you just need to "poll SNMP every 30s", a simple Async/Loop in a management command is lighter.
-   *Ingestion:* If using HTTP Push, you don't need a queue for ingestion. The Async View handles it instantly.

### Database: MySQL
-   **Recommendation:** MySQL (Standard).
-   *Why?* Stick with the existing familiarity and infrastructure.
    -   While it lacks TimescaleDB's native continuous aggregates, MySQL 8.0+ is performant enough for moderate loads.
    -   We can use simple partitioning or manual aggregation jobs if table sizes grow too large.

### SNMP Library: `pysnmp-lextudio` (or `pysnmp` standard)
-   **Recommendation:** `pysnmp-lextudio` (The maintained fork of pysnmp).
-   *Why?* Pure Python, AsyncIO compatible. It fits perfectly into `async def` Django views or consumers.
-   *Alternative:* `easysnmp` (based on Net-SNMP C library) is faster but requires installing system libraries (harder to deploy on some containers). Stay with `pysnmp` unless performance is a bottleneck.

### Summary Comparison Table

| Feature | Current `SNMPHealthMonitor` | Proposed Django Arch | Benefit |
| :--- | :--- | :--- | :--- |
| **Protocol** | WSGI (Flask) | **ASGI (Django + Uvicorn)** | True concurrency for WS & HTTP |
| **Data Flow** | Agent writes to DB directly | **Agent pushes to API** | Decoupling, Security |
| **DB** | MySQL (Standard) | **MySQL** | Consistency |
| **API** | Flask Routes | **Django Ninja (Pydantic)** | Validation, Auto-docs, Speed |
| **Realtime** | SocketIO + UDP | **Django Channels** | Native integration, Scalable |
