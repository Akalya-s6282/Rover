from flask import Blueprint, jsonify

from .db import db
from .models import Rover

stop_all = Blueprint('stop_all',__name__)
# Master route to stop all rovers
@stop_all.route("/master/stop_all", methods=["POST"])
def stop_all_rovers():
    rovers = Rover.query.all()
    for r in rovers:
        r.status = 'stop'
    db.session.commit()
    return jsonify({"stopped": True})
