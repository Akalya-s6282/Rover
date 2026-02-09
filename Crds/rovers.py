from flask import Blueprint, request, jsonify

from .db import db
from .models.models import Rover, Position, Delivery
from datetime import datetime

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
        # Keep rover's latest location in sync for dashboard display
        rover.location_lat = int(lat)
        rover.location_lon = int(lon)

    # Update rover global status
    rover.status = status

    # Update active delivery state if one exists
    active_delivery = Delivery.query.filter(
        Delivery.rover_id == rover.id,
        Delivery.status.in_(["assigned", "in_progress"])
    ).order_by(Delivery.started_at.desc()).first()

    if active_delivery and status != "done":
        if active_delivery.status == "assigned":
            active_delivery.status = "in_progress"

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
        if active_delivery:
            active_delivery.status = "completed"
            active_delivery.completed_at = datetime.utcnow()

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
   
