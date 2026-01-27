from flask import Flask, render_template
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

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # ---- Register blueprints ----
    app.register_blueprint(auth)
    app.register_blueprint(users)
    app.register_blueprint(master)
    app.register_blueprint(rovers)
    app.register_blueprint(test_position)
    # ---- Create DB once ----
    with app.app_context():
        db.create_all()

    # ---- Landing page ----
    @app.route("/")
    def welcome():
        return render_template("welcome.html")

    return app
