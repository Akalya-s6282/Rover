from flask import Blueprint, redirect, request, render_template, url_for

from .db import db
from .models import Rover

assign_coordinates = Blueprint('assign_coordinates', __name__)
# Assign coordinates to rover
@assign_coordinates.route("/rover/<int:rover_id>", methods=["GET", "POST"])
def assign_rover_coordinates(rover_id):
    rover = Rover.query.get_or_404(rover_id)
    if request.method == "POST":
        lat = int(request.form.get("lat"))
        lon = int(request.form.get("lon"))
        rover.location_lat = lat
        rover.location_lon = lon
        rover.status = 'delivering'
        db.session.commit()
        return redirect(url_for('assign_coordinates.assign_rover_coordinates', rover_id=rover.id))
    return render_template("assign.html", rover=rover)
