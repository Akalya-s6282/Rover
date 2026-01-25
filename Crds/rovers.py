from flask import Blueprint, redirect, request, render_template, url_for, session

from .db import db
from .models import Rover

rovers = Blueprint('rovers',__name__)

@rovers.route("/rovers", methods=["GET", "POST"])
def dashboard():
    if request.method == "POST":
        name = request.form.get("name")
        hotel_id = session.get('hotel_id')
        if name and hotel_id:
            new_rover = Rover(name=name, hotel_id=hotel_id)
            db.session.add(new_rover)
            db.session.commit()
        return redirect(url_for('rovers.dashboard'))
    
    hotel_id = session.get('hotel_id')
    rover_list = Rover.query.filter_by(hotel_id=hotel_id).all() if hotel_id else []
    return render_template("index.html", rovers=rover_list)

