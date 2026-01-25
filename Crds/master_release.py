from flask import Blueprint, jsonify

from .db import db
from .models import Rover

master_release = Blueprint('master_release',__name__)
# Master route to release rovers
@master_release.route("/master/release/<int:rover_id>", methods=["POST", "GET"])
def release_rovers(rover_id):
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
