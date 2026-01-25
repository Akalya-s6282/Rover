from flask import Blueprint, jsonify

from .models import RoverConfig

master_config_bp = Blueprint('master_config_bp',__name__)

@master_config_bp.route("/master/config", methods=["GET"])
def master_config():
    config = RoverConfig.query.first_or_404()

    return jsonify({
        "total_latitudes": config.total_latitudes,
        "latitudes": [
            {
                "index": lat.latitude_index,
                "gpio": lat.gpio_pin
            }
            for lat in config.latitudes
        ]
    })


