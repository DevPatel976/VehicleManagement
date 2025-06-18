# Parking Management System

A comprehensive parking management system with user and admin interfaces for managing parking spots, reservations, and user accounts.

## Features

- User authentication (login/register)
- Parking spot reservation system
- Admin dashboard for managing users and parking lots
- Real-time spot availability
- Reservation history and management
- User blocking functionality for admins

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git
- SQLite (included with Python)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/DevPatel976/VehicleManagement.git
cd VehicleManagement
```

### 2. Create and Activate Virtual Environment

#### On Windows:
```bash
python -m venv venv
.\venv\Scripts\activate
```

#### On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root with the following content:

```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URI=sqlite:///parking.db
```

### 5. Initialize the Database

```bash
flask db upgrade
```

### 6. Run the Application

```bash
flask run
```

Visit `http://localhost:5000` in your browser.

## Default Admin Account

To create an admin account, run the following in a Python shell:

```python
from app import create_app, db
from models.user import User

app = create_app()
with app.app_context():
    admin = User(
        username='admin',
        email='admin@example.com',
        is_admin=True
    )
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
```

## Project Structure

```
parking_app/
├── app.py                 # Main application entry point
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── static/               # Static files (CSS, JS, images)
├── templates/            # HTML templates
├── migrations/           # Database migration files
├── models/               # Database models
└── controllers/          # Application routes and logic
```

## API Documentation

### Authentication

- `POST /auth/register` - Register a new user
- `POST /auth/login` - User login
- `GET /auth/logout` - User logout

### User Endpoints

- `GET /user/dashboard` - User dashboard
- `GET /user/reservations` - View user's reservations
- `POST /user/reserve` - Create a new reservation

### Admin Endpoints

- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/users` - Manage users
- `POST /admin/user/<id>/block` - Block a user
- `POST /admin/user/<id>/unblock` - Unblock a user

## Troubleshooting

1. **Database Issues**
   - Delete the database file (`instance/parking.db`)
   - Run `flask db upgrade`
   - Restart the application

2. **Package Installation**
   - Ensure you're using Python 3.8+
   - Try `pip install --upgrade pip`
   - Delete the virtual environment and recreate it

3. **Application Not Starting**
   - Check if port 5000 is available
   - Ensure all environment variables are set
   - Check the application logs for errors

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email support@example.com or open an issue in the GitHub repository.

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
