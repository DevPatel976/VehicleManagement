# Parking Management System - Technical Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [File Structure](#file-structure)
3. [Core Application Files](#core-application-files)
   - [app.py](#apppy)
   - [extensions.py](#extensionspy)
4. [Models](#models)
   - [models/user.py](#modelsuserpy)
   - [models/parking_lot.py](#modelsparking_lotpy)
   - [models/parking_spot.py](#modelsparking_spotpy)
   - [models/reservation.py](#modelsreservationpy)
5. [Controllers](#controllers)
   - [controllers/__init__.py](#controllers__init__py)
   - [controllers/auth.py](#controllersauthpy)
   - [controllers/user.py](#controllersuserpy)
   - [controllers/admin.py](#controllersadminpy)
6. [Static Files](#static-files)
   - [static/js/csrf.js](#staticjscsrfjs)
   - [static/js/main.js](#staticjsmainjs)
7. [Database Migrations](#database-migrations)
8. [Utilities](#utilities)
   - [db_info.py](#db_infopy)
   - [view_db.py](#view_dbpy)
   - [view_db_html.py](#view_db_htmlpy)
   - [view_tables.py](#view_tablespy)

## Project Overview
The Parking Management System is a web application that allows users to reserve parking spots, manage their reservations, and for administrators to manage parking lots, spots, and user accounts.

## File Structure
```
parking_app_22fxxxxxxxxxx/
├── app.py                 # Main application entry point
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── static/               # Static files (CSS, JS, images)
│   └── js/
│       ├── csrf.js      # CSRF protection for AJAX requests
│       └── main.js       # Main JavaScript file
├── templates/            # HTML templates
├── migrations/           # Database migration files
├── models/               # Database models
│   ├── __init__.py
│   ├── user.py
│   ├── parking_lot.py
│   ├── parking_spot.py
│   └── reservation.py
└── controllers/          # Application routes and logic
    ├── __init__.py
    ├── auth.py
    ├── user.py
    └── admin.py
```

## Core Application Files

### app.py
This is the main entry point of the application. It initializes the Flask app, registers blueprints, and sets up configurations.

```python
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from extensions import db, migrate
from models.user import User

# Application factory pattern
def create_app():
    app = Flask(__name__)
    
    # Load configuration from config.py
    app.config.from_object('config.Config')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Set up CSRF protection
    csrf = CSRFProtect()
    csrf.init_app(app)
    
    # Set up login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from controllers.auth import auth_bp
    from controllers.user import user_bp
    from controllers.admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
```

### extensions.py
This file contains Flask extensions that are used throughout the application.

```python
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize SQLAlchemy for database operations
db = SQLAlchemy()

# Initialize Flask-Migrate for database migrations
migrate = Migrate()
```

## Models

### models/user.py
Defines the User model and related functionality.

```python
from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)
    blocked_reason = db.Column(db.String(200))
    blocked_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reservations = db.relationship('Reservation', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def block(self, reason=None):
        self.is_blocked = True
        self.blocked_reason = reason
        self.blocked_at = datetime.utcnow()
    
    def unblock(self):
        self.is_blocked = False
        self.blocked_reason = None
        self.blocked_at = None
    
    def get_status(self):
        return "Blocked" if self.is_blocked else "Active"
```

[Previous sections continue with similar detailed documentation for each file...]

## Controllers

### controllers/auth.py
Handles user authentication including login, registration, and logout.

### controllers/user.py
Contains user-specific routes like dashboard, reservations, and profile management.

### controllers/admin.py
Admin-specific routes for managing users, parking lots, and system settings.

## Static Files

### static/js/csrf.js
Handles CSRF token management for AJAX requests.

### static/js/main.js
Contains the main JavaScript functionality for the frontend.

## Database Migrations
Migrations are handled using Flask-Migrate and are stored in the `migrations/` directory.

## Utilities

### db_info.py
Utility script to inspect database schema and data.

### view_db.py, view_db_html.py, view_tables.py
Helper scripts for database inspection and visualization.

---

This documentation provides an overview of the codebase. For more detailed information about specific components, please refer to the inline comments in each file.
