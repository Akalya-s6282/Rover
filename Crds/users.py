from flask import Blueprint, redirect, request, render_template, url_for, session
from datetime import datetime, timedelta

from .db import db
from .models.models import Rover, Position, RoverConfig, LatitudeGPIO, Delivery, Hotel

users = Blueprint('users',__name__)

@users.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if request.method == "POST":
        id = request.form.get("id")
        name = request.form.get("name")
        hotel_id = session.get('hotel_id')
        if name and hotel_id:
            new_rover = Rover(id=id, name=name, hotel_id=hotel_id)
            db.session.add(new_rover)
            db.session.commit()
        return redirect(url_for('users.dashboard'))
    
    hotel_id = session.get('hotel_id')
    hotel = Hotel.query.get(hotel_id) if hotel_id else None
    hotel_name = hotel.name if hotel else "—"
    rover_list = Rover.query.filter_by(hotel_id=hotel_id).all() if hotel_id else []

    # Dashboard metrics
    active_statuses = ["run", "delivering", "shift"]
    active_rovers = Rover.query.filter(
        Rover.hotel_id == hotel_id,
        Rover.status.in_(active_statuses)
    ).count() if hotel_id else 0

    now = datetime.now()
    day_start = datetime(now.year, now.month, now.day)
    day_end = day_start + timedelta(days=1)

    hour = now.hour
    if 5 <= hour < 12:
        shift = "Morning"
    elif 12 <= hour < 17:
        shift = "Afternoon"
    elif 17 <= hour < 22:
        shift = "Evening"
    else:
        shift = "Night"

    current_time = now.strftime("%H:%M")

    deliveries_today = Delivery.query.filter(
        Delivery.hotel_id == hotel_id,
        Delivery.status == "completed",
        Delivery.completed_at >= day_start,
        Delivery.completed_at < day_end
    ).all() if hotel_id else []

    deliveries_today_count = len(deliveries_today)

    def format_duration(seconds):
        if seconds is None:
            return "—"
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        if minutes >= 60:
            hours = minutes // 60
            minutes = minutes % 60
            return f"{hours}h {minutes}m"
        return f"{minutes}m {secs}s"

    avg_delivery_time = None
    if deliveries_today:
        total_seconds = 0
        for d in deliveries_today:
            if d.completed_at and d.started_at:
                total_seconds += (d.completed_at - d.started_at).total_seconds()
        if total_seconds > 0:
            avg_delivery_time = total_seconds / max(len(deliveries_today), 1)

    avg_delivery_time_str = format_duration(avg_delivery_time)

    order_history = Delivery.query.filter(
        Delivery.hotel_id == hotel_id
    ).order_by(
        Delivery.completed_at.desc().nullslast(),
        Delivery.started_at.desc()
    ).limit(10).all() if hotel_id else []

    return render_template(
        "index.html",
        rovers=rover_list,
        active_rovers=active_rovers,
        deliveries_today=deliveries_today_count,
        avg_delivery_time=avg_delivery_time_str,
        order_history=order_history,
        hotel_name=hotel_name,
        shift=shift,
        current_time=current_time
    )

@users.route("/asssign/<int:rover_id>", methods=["GET", "POST"])
def assign_coordinates(rover_id):
    rover = Rover.query.get_or_404(rover_id)
    if request.method == "POST":
        lat = int(request.form.get("lat"))
        lon = int(request.form.get("lon"))
        rover.location_lat = lat
        rover.location_lon = lon
        rover.status = 'delivering'

        # Close any active delivery for this rover before creating a new one
        active_delivery = Delivery.query.filter(
            Delivery.rover_id == rover.id,
            Delivery.status.in_(["assigned", "in_progress"])
        ).order_by(Delivery.started_at.desc()).first()

        if active_delivery:
            active_delivery.status = "canceled"
            active_delivery.completed_at = datetime.utcnow()

        new_delivery = Delivery(
            rover_id=rover.id,
            hotel_id=rover.hotel_id,
            destination_lat=lat,
            destination_lon=lon,
            status="assigned",
            started_at=datetime.utcnow()
        )
        db.session.add(new_delivery)
        db.session.commit()
        return redirect(url_for('users.assign_coordinates', rover_id=rover.id))
    return render_template("assign.html", rover=rover)


@users.route("/delete/<int:rover_id>", methods=["POST"])
def delete_rover(rover_id):
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

