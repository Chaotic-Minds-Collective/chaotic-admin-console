from flask import Flask, jsonify
import json
import os
import socket

app = Flask(__name__)
CONFIG_PATH = '../data/config.json'
RESTART_PATH = '../data/restart-time.json'

# Your defined grid roles
GRID_TYPES = {
    "C3": "Freeport",
    "C5": "Kraken",
    "B5": "MaxTames",
    "D5": "MaxShips",
    "A5": "Powerstone",
    "E5": "Powerstone",
    "E2": "PvP",
    "E3": "PvP",
    "E4": "PvP"
}

# Check if server responds on the port
def is_port_open(ip, port, timeout=1):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        try:
            sock.connect((ip, port))
            return True
        except:
            return False

@app.route("/api/grid-status")
def grid_status():
    try:
        with open(CONFIG_PATH) as f:
            config = json.load(f)
    except:
        return jsonify({"error": "Config not found"}), 500

    ip = config.get("server_ip", "147.135.97.47")
    rcon_start = config.get("rcon_port_start", 35710)
    rcon_end = config.get("rcon_port_end", 35758)

    grids = {}
    for i, grid_id in enumerate([
        "A1","B1","C1","D1","E1",
        "A2","B2","C2","D2","E2",
        "A3","B3","C3","D3","E3",
        "A4","B4","C4","D4","E4",
        "A5","B5","C5","D5","E5"
    ]):
        port = rcon_start + i
        status = "online" if is_port_open(ip, port) else "offline"
        grids[grid_id] = {
            "status": status,
            "type": GRID_TYPES.get(grid_id, "Normal"),
            "players": 0  # TODO: Add RCON query if needed
        }

    return jsonify(grids)

if __name__ == "__main__":
    app.run(port=5050, debug=False)
