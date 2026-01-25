from .db import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# ====== Hotel / User Account ======
class Hotel(db.Model):
    __tablename__ = 'hotel'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    rovers = db.relationship('Rover', backref='hotel', lazy=True)
    config = db.relationship('RoverConfig', backref='hotel', uselist=False)

    # Password helpers
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# ====== Rover Config / Latitudes / GPIOs ======
class RoverConfig(db.Model):
    __tablename__ = 'rover_config'
    id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)
    total_latitudes = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    latitudes = db.relationship(
        'LatitudeGPIO',
        backref='system',
        cascade='all, delete',
        lazy=True
    )


class LatitudeGPIO(db.Model):
    __tablename__ = 'latitude_gpio'
    id = db.Column(db.Integer, primary_key=True)
    latitude_index = db.Column(db.Integer, nullable=False)
    gpio_pin = db.Column(db.Integer, nullable=False)
    system_id = db.Column(db.Integer, db.ForeignKey('rover_config.id'), nullable=False)


# ====== Rovers ======
class Rover(db.Model):
    __tablename__ = 'rover'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='idle')  # idle, delivering, stop
    location_lat = db.Column(db.Integer, default=0)
    location_lon = db.Column(db.Integer, default=0)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)

    positions = db.relationship('Position', backref='rover', lazy=True)


# ====== Rover Positions ======
class Position(db.Model):
    __tablename__ = 'position'
    id = db.Column(db.Integer, primary_key=True)
    rover_id = db.Column(db.Integer, db.ForeignKey('rover.id'), nullable=False)
    lat = db.Column(db.Integer, nullable=False)
    lon = db.Column(db.Integer, nullable=False)
    phase = db.Column(db.String(10), default='lat')  # lat/lon phase
    status = db.Column(db.String(10), default='normal')  # shift/normal/done
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
