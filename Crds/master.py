from flask import Blueprint, jsonify

from .db import db
from .models.models import Rover, RoverConfig

master = Blueprint('master',__name__)

@master.route("/master/config", methods=["GET"])
def config():
    config = RoverConfig.query.first_or_404()

    return jsonify({
        "total_latitudes": config.total_latitudes,
        "latitudes": [
            {
                "index": lat.latitude_index,
                "gpio": lat.gpio_pin
            }
            for lat in config.latitudes
        ]
    })
# Master route to release rovers
@master.route("/master/release/<int:rover_id>", methods=["POST", "GET"])
def release(rover_id):
    rover = Rover.query.get_or_404(rover_id)

    # Release this rover
    rover.status = "run"

    # Release all other rovers
    Rover.query.update({Rover.status: "run"})

    db.session.commit()

    return jsonify({
        "ok": True,
        "message": f"Rover {rover_id} released",
        "status": "run"
    })
@master.route("/master/stop_all", methods=["POST"])
def stop_all():
    rovers = Rover.query.all()
    for r in rovers:
        r.status = 'stop'
    db.session.commit()
    return jsonify({"stopped": True})