from flask import Flask, request, jsonify
import subprocess
import json
import re

app = Flask(__name__)
CONFIG_PATH = '../data/config.json'

# Load config
def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)

@app.route("/api/config", methods=["GET"])
def get_config():
    return jsonify(load_config())

@app.route("/api/broadcast", methods=["POST"])
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

    config = load_config()
    rcon_pw = config.get("rcon_password", "changeme")
    grid_map = {
        "A1": 35710, "B1": 35711, "C1": 35712, "D1": 35713, "E1": 35714,
        "A2": 35715, "B2": 35716, "C2": 35717, "D2": 35718, "E2": 35719,
        "A3": 35720, "B3": 35721, "C3": 35722, "D3": 35723, "E3": 35724,
        "A4": 35725, "B4": 35726, "C4": 35727, "D4": 35728, "E4": 35729,
        "A5": 35730, "B5": 35731, "C5": 35732, "D5": 35733, "E5": 35734
    }
    port = grid_map[grid]
    cmd = ["mcrcon", "-H", "127.0.0.1", "-P", str(port), "-p", str(rcon_pw), "broadcast", message]
    subprocess.Popen(cmd, shell=False)
    return jsonify({"status": "sent", "grid": grid})

@app.route("/api/start/<grid>", methods=["GET"])
def start_grid(grid):
    if not re.fullmatch(r"[A-E][1-5]", grid):
        return jsonify({"error": "Invalid grid identifier."}), 400
    script = load_config().get("batch_file", "Start_5x5_custom.bat")
    subprocess.Popen([script, grid], shell=False)
    return jsonify({"status": "started", "grid": grid})

@app.route("/api/stop/<grid>", methods=["GET"])
def stop_grid(grid):
    # Placeholder: add stop logic here if implemented
    return jsonify({"status": "stop not implemented", "grid": grid})

if __name__ == "__main__":
    app.run(port=5000, debug=False)
