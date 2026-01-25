from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .models import Hotel
from .db import db

auth = Blueprint("auth", __name__)

@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        hotel_name = request.form.get("hotel_name")

        # Check if user already exists
        if Hotel.query.filter_by(username=username).first():
            flash("Username already exists")
            return redirect(url_for("auth.signup"))

        # Create new hotel account
        hotel = Hotel(name=hotel_name, username=username)
        hotel.set_password(password)
        db.session.add(hotel)
        db.session.commit()

        flash("Account created! You can now login.")
        return redirect(url_for("auth.login"))

    return render_template("signup.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        hotel = Hotel.query.filter_by(username=username).first()

        if hotel and hotel.check_password(password):
            session.clear()
            session["hotel_id"] = hotel.id
            return redirect(url_for("rovers.dashboard"))

        flash("Invalid username or password")

    return render_template("login.html")


@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
