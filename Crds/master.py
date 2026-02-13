from flask import Blueprint, jsonify
from sqlalchemy import desc
from .db import db
from .models.models import Rover, RoverConfig, Position

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

@master.route("/get_positions", methods=["GET"])
def get_positions():
    rovers = Rover.query.all()

    data = []

    for rover in rovers:
        last_pos = (
            Position.query
            .filter_by(rover_id=rover.id)
            .order_by(desc(Position.timestamp))
            .first()
        )

        if last_pos:
            data.append({
                "rover_id": rover.id,
                "lat": last_pos.lat,
                "lon": last_pos.lon,
                "phase": last_pos.phase,
                "status": last_pos.status
            })
        else:
            # Fallback to rover's current fields so dashboard polling still updates
            # even before any Position rows are posted by the device.
            data.append({
                "rover_id": rover.id,
                "lat": rover.location_lat,
                "lon": rover.location_lon,
                "phase": "lat",
                "status": rover.status
            })

    return jsonify(data)

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
