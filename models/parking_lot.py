from extensions import db
from datetime import datetime
from .parking_spot import ParkingSpot
class ParkingLot(db.Model):
    __tablename__ = 'parking_lots'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    max_spots = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    spots = db.relationship('ParkingSpot', backref='parking_lot', lazy=True, cascade='all, delete-orphan')
    def available_spots(self):
        return ParkingSpot.query.filter_by(parking_lot_id=self.id, status='A').count()
    def occupied_spots(self):
        return ParkingSpot.query.filter_by(parking_lot_id=self.id, status='O').count()
    def __repr__(self):
        return f'<ParkingLot {self.name}>'