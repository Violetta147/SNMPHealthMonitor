import json
from datetime import datetime
from typing import List, Dict, Any

# ==========================================
# INPUT: Raw Payload from Manager Service
# ==========================================
# The manager sends a list of metric dictionaries.
# Example:
# [
#   {"name": "sys.name", "value": "raspi-pbl", "ts": 1700000000},
#   {"name": "sys.uptime", "value": 12345, "ts": 1700000000},
#   {"name": "la.load.1m", "value": 0.5, "ts": 1700000000},
#   {"name": "cpu.percent.0", "value": 12.5, "ts": 1700000000},
#   {"name": "mem.total", "value": 1024000, "ts": 1700000000},
#   {"name": "if.in.octets.eth0", "value": 50000, "ts": 1700000000},
#   ...
# ]

def process_metrics(payload: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Process raw metrics from Manager Service to match raspi-pbl_systemstatus.json schema.
    
    Target Schema:
    {
        "device_info": { "online": bool, "last_seen": str, "ip_address": str },
        "system_info": { "sysname": str, "sys_location": str, "sys_uptime": int },
        "load_avg": { "time": str, "load_1m": float, "load_5m": float, "load_15m": float },
        "cpu_percent": [ { "cpu": "cpu0", "percent": float, "time": str }, ... ],
        "net_io": [ { "interface": str, "bytes_recv": int, ... }, ... ],
        "memory": { ... },
        "swap": { ... },
        "temperature": { ... },
        # Historical arrays for sparklines (requires DB history, usually not in single payload)
        "cpu": [ ... ],
        "network": { ... },
        "interfaces": [ ... ]
    }
    """
    
    # 1. Initialize intermediate storage
    metrics_map = {}
    timestamp = None
    sysname = None
    
    # 2. Parse raw payload into a map for easier access
    # Parsing logic: split names like 'cpu.percent.0' -> ['cpu', 'percent', '0']
    for item in payload:
        name = item.get('name')
        value = item.get('value')
        ts = item.get('ts')
        
        # Capture common timestamp and sysname
        if not timestamp and ts:
            timestamp = datetime.fromtimestamp(ts).isoformat()
        if name == 'sys.name':
            sysname = value
            
        metrics_map[name] = value

    # 3. Construct Output Object
    output = {}

    # --- Device Info ---
    # In a real scenario, 'online' and 'ip_address' might come from metadata or DB lookup
    output['device_info'] = {
        "online": True, 
        "last_seen": timestamp,
        "ip_address": "127.0.0.1" # Placeholder or derived from context
    }

    # --- System Info ---
    output['system_info'] = {
        "sysname": sysname,
        "sys_location": metrics_map.get('sys.location', 'Unknown'),
        "sys_uptime": int(metrics_map.get('sys.uptime', 0))
    }

    # --- Load Average ---
    output['load_avg'] = {
        "time": timestamp,
        "load_1m": float(metrics_map.get('la.load.1m', 0.0)),
        "load_5m": float(metrics_map.get('la.load.5m', 0.0)),
        "load_15m": float(metrics_map.get('la.load.15m', 0.0))
    }

    # --- CPU Percent ---
    # Need to iterate to find all cpu cores: cpu.percent.0, cpu.percent.1, ...
    cpu_list = []
    # Pseudo-logic to find dynamic keys
    for key, val in metrics_map.items():
        if key.startswith('cpu.percent.'):
            core_id = key.split('.')[-1] # e.g., '0'
            cpu_list.append({
                "cpu": f"cpu{core_id}",
                "percent": float(val),
                "time": timestamp
            })
    output['cpu_percent'] = sorted(cpu_list, key=lambda x: x['cpu'])

    # --- Network I/O ---
    # Complex part: Raw payload usually has COUNTERS (bytes_recv). 
    # Target JSON has RATES (recv_bytes_s).
    # Logic: 
    #   1. Get current counters from payload.
    #   2. Fetch PREVIOUS counters from Cache/DB for this sysname + interface.
    #   3. Calculate Rate: (Current - Previous) / (Time_Current - Time_Previous)
    net_list = []
    # Identify interfaces from keys like 'if.in.octets.eth0'
    interfaces = set()
    for key in metrics_map:
        if key.startswith('if.in.octets.'):
            interfaces.add(key.split('.')[-1])
            
    for iface in interfaces:
        curr_recv = int(metrics_map.get(f'if.in.octets.{iface}', 0))
        curr_sent = int(metrics_map.get(f'if.out.octets.{iface}', 0))
        
        # PSEUDOCODE: Fetch prev values
        # prev_state = db.get_last_metric(sysname, iface) 
        # recv_rate = (curr_recv - prev_state.recv) / dt
        
        net_list.append({
            "interface": iface,
            "time": timestamp,
            "bytes_recv": curr_recv,
            "bytes_sent": curr_sent,
            "recv_bytes_s": 0.0, # Placeholder for calculated rate
            "send_bytes_s": 0.0,
            "if_oper_status": 1,
            "if_admin_status": 1
        })
    output['net_io'] = net_list

    # --- Memory ---
    output['memory'] = {
        "time": timestamp,
        "total": int(metrics_map.get('mem.total', 0)),
        "used": int(metrics_map.get('mem.used', 0)),
        "free": int(metrics_map.get('mem.free', 0)),
        "percent": float(metrics_map.get('mem.percent', 0.0)), # Often derived: (used/total)*100
        "buffers": int(metrics_map.get('mem.buffers', 0)),
        "cached": int(metrics_map.get('mem.cached', 0)),
        "available": int(metrics_map.get('mem.available', 0)),
        "shared": 0 # If available
    }

    # --- Swap ---
    output['swap'] = {
        "time": timestamp,
        "total": int(metrics_map.get('mem.swap.total', 0)),
        "used": int(metrics_map.get('mem.swap.used', 0)),
        "free": int(metrics_map.get('mem.swap.free', 0)),
        "percent": 0.0 # Calculate: (used/total)*100
    }

    # --- Temperature ---
    output['temperature'] = {
        "time": timestamp,
        "cpu_temp": float(metrics_map.get('sensor.temp', 0.0))
    }
    
    # --- Historical Data (Sparklines) ---
    # These lists (cpu, network) typically require querying the last N minutes from the DB.
    # They cannot be derived solely from the single incoming payload.
    # Logic:
    #   output['cpu'] = db.query_cpu_history(sysname, limit=60)
    #   output['network'] = db.query_network_history(sysname, limit=60)
    output['cpu'] = [] 
    output['network'] = {} 
    output['interfaces'] = list(interfaces)

    return output

if __name__ == "__main__":
    # Test with dummy payload
    dummy_payload = [
        {"name": "sys.name", "value": "raspi-pbl", "ts": 1700000000},
        {"name": "la.load.1m", "value": 0.1, "ts": 1700000000},
        {"name": "cpu.percent.0", "value": 15.0, "ts": 1700000000},
        {"name": "mem.total", "value": 1000, "ts": 1700000000},
    ]
    result = process_metrics(dummy_payload)
    print(json.dumps(result, indent=2))
