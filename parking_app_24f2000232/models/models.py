from db_config import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.Integer, nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')

    spots = db.relationship('ParkingSpot', backref='user', lazy=True)
    bookings = db.relationship('BookingHistory', backref='user_obj', lazy=True)

    def __init__(self, email, password, name, address, pincode, role='user'):
        self.email = email
        self.password = generate_password_hash(password, method='pbkdf2:sha256')
        self.name = name
        self.address = address
        self.pincode = pincode
        self.role = role

    def check_password(self, password):
        return check_password_hash(self.password, password)


class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pincode = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    max_spots = db.Column(db.Integer, nullable=False)
    spots = db.relationship('ParkingSpot', backref='lot', lazy=True)

class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_number = db.Column(db.String(10), nullable=False)
    is_booked = db.Column(db.Boolean, default=False)
    
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    booked_by = db.Column(db.String(100), nullable=True)
    booked_at = db.Column(db.String(100), nullable=True)
    released_at = db.Column(db.String(100), nullable=True)

    bookings = db.relationship('BookingHistory', backref='spot_obj', lazy=True)


class BookingHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_email = db.Column(db.String(100), nullable=False)
    lot_name = db.Column(db.String(100), nullable=False)
    spot_number = db.Column(db.String(10), nullable=False)

    booked_at = db.Column(db.DateTime, nullable=False)
    released_at = db.Column(db.DateTime, nullable=True)
    leaving_at = db.Column(db.DateTime, nullable=True)

    duration = db.Column(db.Float)
    cost = db.Column(db.Float)

    car_number = db.Column(db.String(20))
    car_model = db.Column(db.String(50))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'))
