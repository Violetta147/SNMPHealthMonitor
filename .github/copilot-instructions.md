# SNMPHealthMonitor AI Coding Instructions

## Project Overview
This project is a networked system monitoring solution comprising two distinct components:
1. **`rasberrypi` (Collector):** An SNMP agent/collector that polls devices, writes data to MySQL, and broadcasts real-time updates via UDP.
2. **`query-service` (Backend):** A Flask application that serves a dashboard, provides a REST API for historical data, and bridges UDP notifications to WebSockets for real-time visualization.

## Architecture & Data Flow
Understanding the "Dual-Path" data flow is critical:
*   **Path 1 (History):** The Collector writes metrics **directly** to the MySQL database. The Backend reads from this DB for historical charts/logs.
*   **Path 2 (Real-time):** The Collector sends a **UDP packet** containing the latest metrics to the Backend. The Backend's UDP Listener receives this, processes it (without querying the DB), and pushes it to the Frontend via **Socket.IO**.
    *   *Why?* This decouples real-time visualization latency from database write performance.

## Subproject: `rasberrypi` (The Collector)
*   **Entry Point:** `manager/manager.py` (Runs the polling loop).
*   **SNMP:** Uses `pysnmp` (asyncio) logic in `collectors/snmp.py`. OIDs are loaded from JSON files in `oids/`.
*   **Database:** `db_service/db_writer.py` handles direct MySQL insertions.
*   **Import Handling:** Uses `sys.path.insert(0, ...)` pattern heavily to manage imports. Preserve this when adding new modules.

## Subproject: `query-service` (The Backend)
*   **Entry Point:** `app.py` (Initializes Flask, SocketIO, and the background UDP thread).
*   **Real-time Logic:**
    *   `notifications/udp_listener.py`: Listens for UDP packets.
    *   `services/topic_service.py`: Managing data topics.
    *   `websocket/`: Handles Socket.IO events.
*   **Data Transformation:** `utils/data_transformer.py` converts raw SNMP metrics into dashboard-ready JSON formats.
*   **File Manager:** Contains a custom file management API (`services/file_service.py`) for the frontend.

## Critical Patterns & Conventions
1.  **Configuration:** 
    *   `rasberrypi` uses `config/config.json`.
    *   `query-service` uses `config.py` and environment variables.
2.  **UDP Payload:** The UDP message contains the full metric payload (`{'event': 'new_data', 'metrics': [...]}`), allowing the backend to stream data immediately without DB lookups.
3.  **Imports:** Both subprojects rely on root-relative imports. Always ensure `sys.path` modifications are respected if moving files.

## Common Workflows
*   **Running the Backend:** `python query-service/app.py`
*   **Running the Collector:** `python rasberrypi/manager/manager.py`
*   **Frontend:** HTML/JS in `templates/` and `static/`. No build step required (vanilla JS).

## Future Migration (Context)
*   There is a plan to refactor towards **Django/MySQL**. If working on "Next Gen" features, check `notebooks/django.md` for architectural decisions (Django Ninja, Channels).
