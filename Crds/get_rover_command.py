from flask import Blueprint, jsonify

from .models import Rover

get_rover_command = Blueprint('get_rover_command',__name__)
# ESP polls this route to get latest command
@get_rover_command.route("/rover/<int:rover_id>/get")
def fetch_rover_command(rover_id):
    rover = Rover.query.get_or_404(rover_id)
    return jsonify({
        "lat": rover.location_lat,
        "lon": rover.location_lon,
        "status": rover.status
    })
