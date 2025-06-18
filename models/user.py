from flask_login import UserMixin
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)
    blocked_reason = db.Column(db.String(200), nullable=True)
    blocked_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reservations = db.relationship('Reservation', backref='user', lazy=True)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def get_id(self):
        return str(self.id)
    def block(self, reason=None):
        self.is_blocked = True
        self.blocked_reason = reason
        self.blocked_at = datetime.utcnow()
        db.session.commit()
    def unblock(self):
        self.is_blocked = False
        self.blocked_reason = None
        self.blocked_at = None
        db.session.commit()
    def get_status(self):
        if self.is_blocked:
            return f'Blocked (Reason: {self.blocked_reason or "Not specified"})'
        return 'Active'
    def __repr__(self):
        return f'<User {self.username}>'