from flask import Flask, render_template
import os
from .db import db

# blueprints
from .users import users
from .auth import auth
from .master import master
from .test_position import test_position
from .rovers import rovers



def create_app():

    app = Flask(__name__)
    app.secret_key = "super-secret-key-change-later"   # required for login session

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "sqlite:///site.db",
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # ---- Register blueprints ----
    app.register_blueprint(auth)
    app.register_blueprint(users)
    app.register_blueprint(master)
    app.register_blueprint(rovers)
    app.register_blueprint(test_position)
    # ---- Create DB once ----
    # Skip auto-migration if DB is not reachable (common on first deploy)
    if os.getenv("SKIP_DB_INIT") != "1":
        try:
            with app.app_context():
                db.create_all()
        except Exception as exc:
            print(f"DB init skipped: {exc}")

    # ---- Landing page ----
    @app.route("/")
    def welcome():
        return render_template("welcome.html")

    return app
