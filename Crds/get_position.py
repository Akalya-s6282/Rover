from flask import Blueprint, jsonify

from .models import Rover, Position

get_position = Blueprint('get_position',__name__)
@get_position.route("/rover/<int:rover_id>/position", methods=["GET"])
def get_rover_position(rover_id):
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