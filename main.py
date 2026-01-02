from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Flask cloud server running"

@app.route("/send")
def send():
    rover = request.args.get("rover")
    a = request.args.get("a")
    b = request.args.get("b")

    return jsonify({
        "status": "OK",
        "rover": rover,
        "a": a,
        "b": b
    })

@app.route("/get")
def get():
    return jsonify({
        "status": "OK",
        "a": 3,
        "b": 2
    })

# 🚨 CRITICAL CHANGE
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
