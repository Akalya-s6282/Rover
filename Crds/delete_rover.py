from flask import Blueprint, redirect, url_for

from .db import db
from .models import Rover, Position

delete_rover = Blueprint('delete_rover',__name__)
@delete_rover.route("/rover/<int:rover_id>/delete", methods=["POST"])
def delete_rover_func(rover_id):
    rover = Rover.query.get_or_404(rover_id)

    # delete child rows first (important)
    Position.query.filter_by(rover_id=rover.id).delete()

    # delete rover
    db.session.delete(rover)
    db.session.commit()

    return redirect(url_for("rovers.dashboard"))