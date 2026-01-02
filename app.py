from flask import Flask, render_template, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import atexit

app = Flask(__name__)

# ===== In-memory storage of commands =====
# For multiple rovers, use a dict: {'rover1': {...}, 'rover2': {...}}
rover_command = {
    "lat": 0.0,
    "lon": 0.0,
    "status": "idle"   # 'start' or 'stop'
}

# ===== Routes =====
@app.route("/")
def dashboard():
    # Load UI page
    return render_template("index.html", command=rover_command)

@app.route("/set", methods=["POST"])
def set_coordinates():
    # Receive coordinates from web UI
    data = request.get_json()
    lat = data.get("lat")
    lon = data.get("lon")
    cmd = data.get("status", "start")

    rover_command["lat"] = lat
    rover_command["lon"] = lon
    rover_command["status"] = cmd

    return jsonify({"success": True, "message": "Command updated", "command": rover_command})

@app.route("/get")
def get_command():
    # ESP polls this endpoint to get latest command
    return jsonify(rover_command)

@app.route("/ping")
def ping():
    return "pong"

# ===== Keep-alive function =====
def keep_alive():
    try:
        url = "https://your-render-url.onrender.com/ping"
        r = requests.get(url, timeout=5)
        print(f"Keep-alive ping sent, status: {r.status_code}")
    except Exception as e:
        print(f"Keep-alive error: {e}")

# ===== Scheduler =====
scheduler = BackgroundScheduler()
scheduler.add_job(func=keep_alive, trigger="interval", minutes=15)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

# ===== Run app =====
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
