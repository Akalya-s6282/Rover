from flask import Blueprint, redirect, request, render_template, url_for, session

from .db import db
from .models.models import Rover, Position, RoverConfig, LatitudeGPIO

users = Blueprint('users',__name__)

@users.route("/rovers", methods=["GET", "POST"])
def dashboard():
    if request.method == "POST":
        name = request.form.get("name")
        hotel_id = session.get('hotel_id')
        if name and hotel_id:
            new_rover = Rover(name=name, hotel_id=hotel_id)
            db.session.add(new_rover)
            db.session.commit()
        return redirect(url_for('users.dashboard'))
    
    hotel_id = session.get('hotel_id')
    rover_list = Rover.query.filter_by(hotel_id=hotel_id).all() if hotel_id else []
    return render_template("index.html", rovers=rover_list)

@users.route("/rover/<int:rover_id>", methods=["GET", "POST"])
def assign_coordinates(rover_id):
    rover = Rover.query.get_or_404(rover_id)
    if request.method == "POST":
        lat = int(request.form.get("lat"))
        lon = int(request.form.get("lon"))
        rover.location_lat = lat
        rover.location_lon = lon
        rover.status = 'delivering'
        db.session.commit()
        return redirect(url_for('users.assign_coordinates', rover_id=rover.id))
    return render_template("assign.html", rover=rover)


@users.route("/rover/<int:rover_id>/delete", methods=["POST"])
def delete_rover_func(rover_id):
    rover = Rover.query.get_or_404(rover_id)

    # delete child rows first (important)
    Position.query.filter_by(rover_id=rover.id).delete()

    # delete rover
    db.session.delete(rover)
    db.session.commit()

    return redirect(url_for("users.dashboard"))
@users.route("/system/setup", methods=["GET", "POST"])
def configure_system():
    if request.method == "POST":
        action = request.form.get("action")
        print(f"DEBUG: Action = {action}")
        print(f"DEBUG: Form data = {request.form}")

        config = RoverConfig.query.first()

        # Action 1: Save total latitudes
        if action == "save_total":
            total = request.form.get("total_latitudes")
            print(f"DEBUG: Total latitudes from form = {total}")
            
            if total:
                total = int(total)
                if not config:
                    config = RoverConfig(total_latitudes=total, hotel_id=session.get('hotel_id'))
                    db.session.add(config)
                    print(f"DEBUG: Creating new config with total_latitudes = {total}")
                else:
                    config.total_latitudes = total
                    print(f"DEBUG: Updating existing config with total_latitudes = {total}")
                
                db.session.commit()
                print("DEBUG: Config saved successfully")
                # Post/Redirect/Get — redirect so the GET will render GPIO inputs
                return redirect(url_for("users.configure_system", show_gpio=1))

        # Action 2: Save GPIO configuration
        elif action == "save_gpio":
            # If no config exists yet, create one using the provided total
            lat_indexes = request.form.getlist("latitude_index")
            gpio_pins = request.form.getlist("gpio_pin")
            print(f"DEBUG: GPIO - lat_indexes = {lat_indexes}, gpio_pins = {gpio_pins}")

            if not config:
                # try to get total from the form or fallback to lat_indexes length
                total = request.form.get('total_latitudes')
                if total:
                    total = int(total)
                else:
                    total = len(lat_indexes)

                config = RoverConfig(total_latitudes=total, hotel_id=session.get('hotel_id'))
                db.session.add(config)
                db.session.commit()
                print(f"DEBUG: Created new config with total_latitudes={total}")

            # Clear old GPIO mappings
            LatitudeGPIO.query.filter_by(system_id=config.id).delete()

            for lat, gpio in zip(lat_indexes, gpio_pins):
                db.session.add(
                    LatitudeGPIO(
                        latitude_index=int(lat),
                        gpio_pin=int(gpio),
                        system_id=config.id
                    )
                )

            db.session.commit()
            print("DEBUG: GPIO Configuration saved successfully")
            return redirect(url_for("users.dashboard"))

    # GET request - query config fresh
    config = RoverConfig.query.first()
    print(f"DEBUG: GET request - config = {config}")
    if config:
        print(f"DEBUG: Config total_latitudes = {config.total_latitudes}")

    show_gpio = request.args.get('show_gpio')
    return render_template("system_setup.html", config=config, show_gpio=show_gpio)

