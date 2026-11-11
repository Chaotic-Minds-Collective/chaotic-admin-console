import hmac
import json
import os
import re
import subprocess
from functools import wraps
from pathlib import Path

from flask import Flask, jsonify, request

app = Flask(__name__)
CONFIG_PATH = Path(__file__).resolve().parents[1] / "data" / "config.json"
ADMIN_UI_ORIGIN = os.environ.get("ADMIN_UI_ORIGIN", "http://localhost:3000")


def load_config():
    with CONFIG_PATH.open(encoding="utf-8") as config_file:
        return json.load(config_file)


def admin_required(handler):
    @wraps(handler)
    def wrapped(*args, **kwargs):
        token = os.environ.get("ADMIN_API_TOKEN", "")
        if len(token) < 32:
            return jsonify({"error": "ADMIN_API_TOKEN must be configured with at least 32 characters."}), 503
        expected = f"Bearer {token}"
        provided = request.headers.get("Authorization", "")
        if not hmac.compare_digest(provided, expected):
            return jsonify({"error": "A valid admin API token is required."}), 401
        return handler(*args, **kwargs)

    return wrapped


@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin")
    if origin == ADMIN_UI_ORIGIN:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Vary"] = "Origin"
    return response


@app.route("/api/config", methods=["GET"])
def get_config():
    config = load_config()
    public_keys = ("server_ip", "rcon_port_start", "rcon_port_end")
    return jsonify({key: config[key] for key in public_keys if key in config})


@app.route("/api/broadcast", methods=["POST"])
@admin_required
def broadcast_message():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required."}), 400

    grid = data.get("grid")
    message = data.get("message")
    if not isinstance(grid, str) or not re.fullmatch(r"[A-E][1-5]", grid):
        return jsonify({"error": "Invalid grid identifier."}), 400
    if not isinstance(message, str) or not message.strip() or len(message) > 500:
        return jsonify({"error": "Message must be a non-empty string of at most 500 characters."}), 400
    if re.search(r"[\x00-\x1f\x7f;\"\\]", message):
        return jsonify({"error": "Message contains unsupported control or command-delimiter characters."}), 400

    rcon_password = os.environ.get("RCON_PASSWORD", "")
    if not rcon_password:
        return jsonify({"error": "RCON_PASSWORD must be configured on the server."}), 503

    grid_map = {
        "A1": 35710, "B1": 35711, "C1": 35712, "D1": 35713, "E1": 35714,
        "A2": 35715, "B2": 35716, "C2": 35717, "D2": 35718, "E2": 35719,
        "A3": 35720, "B3": 35721, "C3": 35722, "D3": 35723, "E3": 35724,
        "A4": 35725, "B4": 35726, "C4": 35727, "D4": 35728, "E4": 35729,
        "A5": 35730, "B5": 35731, "C5": 35732, "D5": 35733, "E5": 35734,
    }
    command = ["mcrcon", "-H", "127.0.0.1", "-P", str(grid_map[grid]), "-p", rcon_password, "-t"]
    try:
        result = subprocess.run(
            command,
            input=f"broadcast {message}\nQ\n",
            text=True,
            capture_output=True,
            timeout=10,
            shell=False,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return jsonify({"error": "RCON command timed out."}), 504
    if result.returncode != 0:
        return jsonify({"error": "RCON command failed."}), 502
    return jsonify({"status": "sent", "grid": grid})


@app.route("/api/start/<grid>", methods=["POST"])
@admin_required
def start_grid(grid):
    if not re.fullmatch(r"[A-E][1-5]", grid):
        return jsonify({"error": "Invalid grid identifier."}), 400
    script = load_config().get("batch_file", "Start_5x5_custom.bat")
    try:
        subprocess.Popen([script, grid], shell=False)
    except OSError:
        app.logger.exception("Unable to start grid %s", grid)
        return jsonify({"error": "Unable to start the grid."}), 500
    return jsonify({"status": "started", "grid": grid})


@app.route("/api/stop/<grid>", methods=["POST"])
@admin_required
def stop_grid(grid):
    if not re.fullmatch(r"[A-E][1-5]", grid):
        return jsonify({"error": "Invalid grid identifier."}), 400
    return jsonify({"status": "stop not implemented", "grid": grid}), 501


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
