from flask import Blueprint, jsonify

from .db import db
from .models.models import Rover, Position

test_position = Blueprint('test_position',__name__)
@test_position.route("/test/rover/<int:rover_id>/position")
def insert_test_position(rover_id):
    rover = Rover.query.get_or_404(rover_id)

    pos = Position(
        rover_id=rover.id,
        lat=2,
        lon=3,
        phase="lat",
        status="run"
    )

    rover.status = "run"

    db.session.add(pos)
    db.session.commit()

    return jsonify({
        "ok": True,
        "message": "Test position inserted",
        "rover": rover.id
    })

    


