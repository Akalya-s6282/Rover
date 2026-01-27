from flask import Blueprint, request, jsonify

from .db import db
from .models.models import Rover, Position

rovers = Blueprint('rovers',__name__)

@rovers.route("/rover/<int:rover_id>/get")
def fetch(rover_id):
    rover = Rover.query.get_or_404(rover_id)
    return jsonify({
        "lat": rover.location_lat,
        "lon": rover.location_lon,
        "status": rover.status
    })
# View last known position
@rovers.route("/rover/<int:rover_id>/position", methods=["GET"])
def get_position(rover_id):
    rover = Rover.query.get_or_404(rover_id)

    last_pos = Position.query.filter_by(rover_id=rover_id)\
                             .order_by(Position.id.desc())\
                             .first()

    if not last_pos:
        return jsonify({
            "rover": rover_id,
            "message": "No position data yet"
        })
       

    return jsonify({
        "rover": rover.id,
        "lat": last_pos.lat,
        "lon": last_pos.lon,
        "phase": last_pos.phase,
        "status": last_pos.status,
        "time": last_pos.timestamp.isoformat()
    })
# ESP updates position after reaching a step
@rovers.route("/rover/<int:rover_id>/position", methods=["POST"])
def update_position(rover_id):
    rover = Rover.query.get_or_404(rover_id)
    data = request.get_json(force=True)

    lat = data.get("lat")
    lon = data.get("lon")
    phase = data.get("phase", "lat")     # lat | lon | done
    status = data.get("status", "run")   # run | shift | stop

    # Store position ONLY if lat & lon exist
    if lat is not None and lon is not None:
        pos = Position(
            rover_id=rover.id,
            lat=int(lat),
            lon=int(lon),
            phase=phase,
            status=status
        )
        db.session.add(pos)

    # Update rover global status
    rover.status = status

    # 🚦 MASTER CONTROL LOGIC
    if status == "shift":
        # stop all others
        Rover.query.filter(
            Rover.id != rover.id
        ).update({Rover.status: "stop"})

    if status == "run":
        # release others
        Rover.query.update({Rover.status: "run"})

    if status == "done":
        Position.query.filter_by(rover_id=rover.id).delete()
        rover.status = "idle"   # or "completed"
        db.session.commit()

        return jsonify({
            "ok": True,
            "message": "Delivery completed. Positions cleared."
        })
    db.session.commit()

    return jsonify({
        "ok": True,
        "rover": rover.id,
        "status": status,
        "phase": phase
    })
   
