from extensions import db
from datetime import datetime
from sqlalchemy.orm import relationship, backref
class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id'), nullable=False)
    spot = relationship('ParkingSpot', back_populates='reservations')
    check_in = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    check_out = db.Column(db.DateTime)
    amount = db.Column(db.Float)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_reversed = db.Column(db.Boolean, default=False)
    reversed_at = db.Column(db.DateTime)
    reversal_reason = db.Column(db.String(100))
    reversal_notes = db.Column(db.Text)
    vehicle_registration = db.Column(db.String(20))
    drivers_license = db.Column(db.String(20))
    payment_method = db.Column(db.String(20), default='cash')
    payment_status = db.Column(db.String(20), default='pending')
    payment_date = db.Column(db.DateTime)
    transaction_id = db.Column(db.String(50))
    def calculate_amount(self, price_per_hour):
        if not self.check_out:
            return 0
        duration = (self.check_out - self.check_in).total_seconds() / 3600
        return round(duration * price_per_hour, 2)
    def __repr__(self):
        return f'<Reservation {self.id} - User {self.user_id} - Spot {self.spot_id}>'