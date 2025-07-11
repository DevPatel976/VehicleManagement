from extensions import db
from datetime import datetime
class ParkingSpot(db.Model):
    __tablename__ = 'parking_spots'
    id = db.Column(db.Integer, primary_key=True)
    spot_number = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(1), default='A')
    parking_lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reservations = db.relationship('Reservation', back_populates='spot', lazy=True)
    def is_available(self):
        return self.status == 'A'
    def __repr__(self):
        return f'<ParkingSpot {self.spot_number} ({self.status})>'