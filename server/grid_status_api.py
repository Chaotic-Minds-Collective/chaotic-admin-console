from datetime import datetime
import json
import os
from pathlib import Path
import socket

from flask import Flask, jsonify, request

app = Flask(__name__)
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
CONFIG_PATH = DATA_DIR / "config.json"
RESTART_PATH = DATA_DIR / "restart-time.json"
DASHBOARD_ORIGIN = os.environ.get("DASHBOARD_ORIGIN", "http://localhost:3000")

GRID_TYPES = {
    "C3": "Freeport",
    "C5": "Kraken",
    "B5": "MaxTames",
    "D5": "MaxShips",
    "A5": "Powerstone",
    "E5": "Powerstone",
    "E2": "PvP",
    "E3": "PvP",
    "E4": "PvP",
}
GRID_IDS = [f"{row}{column}" for row in "ABCDE" for column in "12345"]


def is_port_open(ip, port, timeout=1):
    """Check whether a TCP connection succeeds within the given timeout."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        try:
            sock.connect((ip, port))
            return True
        except OSError:
            return False


@app.after_request
def add_cors_headers(response):
    """Allow dashboard requests only from the configured browser origin."""
    origin = request.headers.get("Origin")
    if origin == DASHBOARD_ORIGIN:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"
    return response


@app.route("/api/grid-status")
def grid_status():
    """Read grid configuration and return TCP availability for each grid."""
    try:
        with CONFIG_PATH.open(encoding="utf-8") as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        return jsonify({"error": "Config not found"}), 500
    except (OSError, json.JSONDecodeError):
        app.logger.exception("Unable to load grid status config")
        return jsonify({"error": "Unable to load config"}), 500

    ip = config.get("server_ip", "127.0.0.1")
    rcon_start = config.get("rcon_port_start", 35710)

    grids = {}
    for index, grid_id in enumerate(GRID_IDS):
        port = rcon_start + index
        status = "online" if is_port_open(ip, port) else "offline"
        grids[grid_id] = {
            "status": status,
            "type": GRID_TYPES.get(grid_id, "Normal"),
            "players": 0,
        }

    return jsonify(grids)


@app.route("/api/restart-time")
def restart_time():
    """Return a timezone-aware restart schedule or an error for missing or invalid data."""
    try:
        with RESTART_PATH.open(encoding="utf-8") as restart_file:
            data = json.load(restart_file)
    except FileNotFoundError:
        return jsonify({"error": "Restart time is not configured."}), 404
    except (OSError, json.JSONDecodeError):
        app.logger.exception("Unable to load restart schedule")
        return jsonify({"error": "Unable to load restart schedule."}), 500

    if not isinstance(data, dict) or not isinstance(data.get("restart_time_utc"), str):
        return jsonify({"error": "Restart schedule must contain restart_time_utc."}), 500
    try:
        timestamp = datetime.fromisoformat(data["restart_time_utc"].replace("Z", "+00:00"))
        if timestamp.utcoffset() is None:
            raise ValueError("A timezone offset is required")
    except ValueError:
        return jsonify({"error": "restart_time_utc must be a valid ISO 8601 timestamp."}), 500
    return jsonify(data)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=False)
