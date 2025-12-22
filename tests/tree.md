📦query-service
 ┣ 📂api
 ┃ ┣ 📜router.py
 ┃ ┗ 📜__init__.py
 ┣ 📂db

 ┃ ┣ 📜connection.py
 ┃ ┣ 📜queries.py
 ┃ ┗ 📜__init__.py
 ┣ 📂logs
 ┃ ┣ 📜2025-12-20.log
 ┃ ┣ 📜2025-12-21.log
 ┃ ┣ 📜raspi-pbl_disk.json
 ┃ ┣ 📜raspi-pbl_diskio.json
 ┃ ┣ 📜raspi-pbl_network.json
 ┃ ┗ 📜raspi-pbl_systemstatus.json
 ┣ 📂notifications
 ┃ ┣ 📜udp_listener.py
 ┃ ┣ 📜websocket_manager.py
 ┃ ┣ 📜udp_listener.py
 ┃ ┗ 📜__init__.py
 ┣ 📂services
 ┃ ┣ �device_service.py
 ┃ ┣ 📜payload_transformer.py
 ┃ ┣ 📜pdf_service.py
 ┃ ┣ 📜plot_service.py
 ┃ ┣ 📜task_manager.py
 ┃ ┣ 📜device_service.py
 ┃ ┣ 📜pdf_service.py
 ┃ ┣ 📜plot_service.py
 ┃ ┣ 📜topic_service.py
 ┃ ┗ 📜__init__.py
 ┣ 📂static
 ┃ ┣ 📂css
 ┃ ┃ ┗ 📜dashboard.css
 ┃ ┗ 📂js
 ┃ ┃ ┣ 📂dashboard
 ┃ ┃ ┃ ┣ 📜base.js
 ┃ ┃ ┃ ┣ 📜disk.js
 ┃ ┃ ┃ ┣ 📜diskio.js
 ┃ ┃ ┃ ┣ 📜history.js
 ┃ ┃ ┃ ┣ 📜network.js
 ┃ ┃ ┃ ┗ 📜systemstatus.js
 ┃ ┃ ┣ 📜dashboard-ui.js
 ┃ ┃ ┣ 📜dashboard.js
 ┃ ┃ ┣ 📜data-processor.js
 ┃ ┃ ┣ 📜memory-chart.js
 ┃ ┃ ┣ 📜memory-percent-chart.js
 ┃ ┃ ┣ 📜system-chart.js
 ┃ ┃ ┗ 📜websocket-manager.js
 ┣ 📂template
 ┃ ┣ 📜404.html
 ┃ ┣ 📜base.html
 ┃ ┣ 📜dashboard.html
 ┃ ┣ 📜disk.html
 ┃ ┣ 📜diskio.html
 ┃ ┣ 📜history.html
 ┃ ┗ 📜network.html
 ┣ 📂utils
 ┃ ┣ 📜logging.py
 ┃ ┣ 📜serialize.py
 ┃ ┣ 📜time_range.py
 ┃ ┗ 📜__init__.py
 ┣ 📂web
 ┃ ┣ 📜router.py
 ┃ ┗ 📜__init__.py
 ┣ 📂websocket
 ┃ ┣ 📜socket_handlers.py
 ┃ ┣ 📜websocket_manager.py
 ┃ ┗ 📜__init__.py
 ┣ 📜app.py
 ┣ 📜config.py
 ┣ 📜debug_db.py
 ┣ 📜pbl4.conf
 ┗ 📜requirements.txt