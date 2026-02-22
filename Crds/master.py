from flask import Blueprint, jsonify, request, session, abort
from sqlalchemy import desc
from .db import db
from .models.models import Rover, RoverConfig, Position, Hotel

master = Blueprint('master',__name__)

def resolve_hotel(master_id=None):
    master_id = (master_id or request.args.get("master_id") or "").strip()
    if master_id:
        hotel = Hotel.query.filter_by(master_id=master_id).first()
        if not hotel:
            abort(404, description="Invalid master_id")
        return hotel

    hotel_id = session.get("hotel_id")
    if hotel_id:
        hotel = Hotel.query.get(hotel_id)
        if hotel:
            return hotel

    abort(400, description="master_id is required")

@master.route("/master/config/<master_id>", methods=["GET"])
def config(master_id):
    hotel = resolve_hotel(master_id)
    config = RoverConfig.query.filter_by(hotel_id=hotel.id).first_or_404()

    return jsonify({
        "master_id": hotel.master_id,
        "total_latitudes": config.total_latitudes,
        "latitudes": [
            {
                "index": lat.latitude_index,
                "gpio": lat.gpio_pin
            }
            for lat in config.latitudes
        ],
        
    })

@master.route("/get_positions/<master_id>", methods=["GET"])
def get_positions(master_id):
    hotel = resolve_hotel(master_id)
    rovers = Rover.query.filter_by(hotel_id=hotel.id).all()

    data = []

    for rover in rovers:
        last_pos = (
            Position.query
            .filter_by(rover_id=rover.id)
            .order_by(desc(Position.timestamp))
            .first()
        )

        if last_pos:
            data.append({
                "rover_id": rover.id,
                "hotel_id": rover.hotel_id,
                "master_id": hotel.master_id,
                "lat": last_pos.lat,
                "lon": last_pos.lon,
                "phase": last_pos.phase,
                "status": last_pos.status
            })
        else:
            # Fallback to rover's current fields so dashboard polling still updates
            # even before any Position rows are posted by the device.
            data.append({
                "rover_id": rover.id,
                "hotel_id": rover.hotel_id,
                "master_id": hotel.master_id,
                "lat": rover.location_lat,
                "lon": rover.location_lon,
                "phase": "lat",
                "status": rover.status
            })

    return jsonify(data)

# Master route to release rovers
@master.route("/master/release/<int:rover_id>", defaults={"master_id": None}, methods=["POST", "GET"])
@master.route("/master/release/<int:rover_id>/<master_id>", methods=["POST", "GET"])
def release(rover_id, master_id):
    rover = Rover.query.get_or_404(rover_id)
    hotel = resolve_hotel(master_id) if master_id else Hotel.query.get_or_404(rover.hotel_id)
    if rover.hotel_id != hotel.id:
        return jsonify({"ok": False, "message": "Rover does not belong to this master"}), 403

    # Release this rover
    rover.status = "run"

    # Release rovers for this hotel only
    Rover.query.filter_by(hotel_id=hotel.id).update({Rover.status: "run"})

    db.session.commit()

    return jsonify({
        "ok": True,
        "message": f"Rover {rover_id} released",
        "status": "run"
    })
@master.route("/master/stop_all/<master_id>", methods=["POST"])
def stop_all(master_id):
    hotel = resolve_hotel(master_id)
    rovers = Rover.query.filter_by(hotel_id=hotel.id).all()
    for r in rovers:
        if r.status != 'shift':
            r.status = 'stop'
    db.session.commit()
    return jsonify({"stopped": True})
