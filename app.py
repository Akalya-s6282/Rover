from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rovers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ====== Models ======
class Rover(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='idle')  # idle, delivering, stop
    location_lat = db.Column(db.Integer, default=0)
    location_lon = db.Column(db.Integer, default=0)
    positions = db.relationship('Position', backref='rover', lazy=True)

class Position(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rover_id = db.Column(db.Integer, db.ForeignKey('rover.id'), nullable=False)
    lat = db.Column(db.Integer, nullable=False)
    lon = db.Column(db.Integer, nullable=False)
    phase = db.Column(db.String(10), default='lat')  # lat/lon phase
    status = db.Column(db.String(10), default='normal')  # shift/normal
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ====== Routes ======

# Dashboard: show all rovers + create new
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        if name:
            new_rover = Rover(name=name)
            db.session.add(new_rover)
            db.session.commit()
        return redirect(url_for('index'))
    
    rovers = Rover.query.all()
    position = Position.query.all()
    print(position)
    return render_template("index.html", rovers=rovers, position=position)

# Delete rover
@app.route("/rover/<int:rover_id>/delete", methods=["POST"])
def delete_rover(rover_id):
    rover = Rover.query.get_or_404(rover_id)

    # delete child rows first (important)
    Position.query.filter_by(rover_id=rover.id).delete()

    # delete rover
    db.session.delete(rover)
    db.session.commit()

    return redirect(url_for("index"))

# Assign coordinates to rover
@app.route("/rover/<int:rover_id>", methods=["GET", "POST"])
def assign_coordinates(rover_id):
    rover = Rover.query.get_or_404(rover_id)
    if request.method == "POST":
        lat = int(request.form.get("lat"))
        lon = int(request.form.get("lon"))
        rover.location_lat = lat
        rover.location_lon = lon
        rover.status = 'delivering'
        db.session.commit()
        # Redirect to ESP polling route
        return redirect(url_for('get_rover_command', rover_id=rover.id))
    return render_template("assign.html", rover=rover)

# ESP polls this route to get latest command
@app.route("/rover/<int:rover_id>/get")
def get_rover_command(rover_id):
    rover = Rover.query.get_or_404(rover_id)
    return jsonify({
        "lat": rover.location_lat,
        "lon": rover.location_lon,
        "status": rover.status
    })

# ESP updates position after reaching a step
@app.route("/rover/<int:rover_id>/position", methods=["POST"])
def update_position(rover_id):
    rover = Rover.query.get_or_404(rover_id)
    data = request.get_json(force=True)

    lat = data.get("lat")
    lon = data.get("lon")
    phase = data.get("phase", "lat")     # lat | lon | done
    status = data.get("status", "run")   # run | shift | stop

    # Store position ONLY if lat & lon exist
    if lat is not None and lon is not None:
        pos = Position(
            rover_id=rover.id,
            lat=int(lat),
            lon=int(lon),
            phase=phase,
            status=status
        )
        db.session.add(pos)

    # Update rover global status
    rover.status = status

    # 🚦 MASTER CONTROL LOGIC
    if status == "shift":
        # stop all others
        Rover.query.filter(
            Rover.id != rover.id
        ).update({Rover.status: "stop"})

    if status == "run":
        # release others
        Rover.query.update({Rover.status: "run"})

    if status == "done":
        Position.query.filter_by(rover_id=rover.id).delete()
        rover.status = "idle"   # or "completed"
        db.session.commit()

        return jsonify({
            "ok": True,
            "message": "Delivery completed. Positions cleared."
        })
    db.session.commit()

    return jsonify({
        "ok": True,
        "rover": rover.id,
        "status": status,
        "phase": phase
    })
   

@app.route("/rover/<int:rover_id>/position", methods=["GET"])
def get_position(rover_id):
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

@app.route("/test/rover/<int:rover_id>/position")
def test_insert_position(rover_id):
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

    



# Master route to release rovers
@app.route("/master/release/<int:rover_id>", methods=["POST", "GET"])
def master_release(rover_id):
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

# Master route to stop all rovers
@app.route("/master/stop_all", methods=["POST"])
def stop_all():
    rovers = Rover.query.all()
    for r in rovers:
        r.status = 'stop'
    db.session.commit()
    return jsonify({"stopped": True})

# Initialize DB
@app.before_request
def create_tables():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
