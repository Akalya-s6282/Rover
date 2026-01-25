from flask import Flask, render_template
from .db import db

# blueprints
from .assign_coordinates import assign_coordinates
from .rovers import rovers
from .auth import auth
from .update_position import update_position
from .master_release import master_release
from .stop_all import stop_all
from .get_rover_command import get_rover_command
from .master_config import master_config_bp as master_config
from .system_setup import system_setup
from .test_position import test_position
from .delete_rover import delete_rover
from .get_position import get_position


def create_app():

    app = Flask(__name__)
    app.secret_key = "super-secret-key-change-later"   # required for login session

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # ---- Register blueprints ----
    app.register_blueprint(auth)
    app.register_blueprint(rovers)
    app.register_blueprint(assign_coordinates)
    app.register_blueprint(update_position)
    app.register_blueprint(master_release)
    app.register_blueprint(stop_all)
    app.register_blueprint(get_rover_command)
    app.register_blueprint(master_config)
    app.register_blueprint(system_setup)
    app.register_blueprint(test_position)
    app.register_blueprint(delete_rover)
    app.register_blueprint(get_position)

    # ---- Create DB once ----
    with app.app_context():
        db.create_all()

    # ---- Landing page ----
    @app.route("/")
    def welcome():
        return render_template("welcome.html")

    return app
