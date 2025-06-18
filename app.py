import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for
from flask_login import current_user
from flask_wtf.csrf import CSRFProtect, generate_csrf
from dotenv import load_dotenv
from extensions import db, login_manager
load_dotenv()
def setup_config(app):
    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev-key-123'),
        SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'sqlite:///parking.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        WTF_CSRF_SECRET_KEY=os.getenv('WTF_CSRF_SECRET_KEY'),
        WTF_CSRF_TIME_LIMIT=int(os.getenv('WTF_CSRF_TIME_LIMIT', '3600')),
        SESSION_TYPE=os.getenv('SESSION_TYPE', 'filesystem'),
        SESSION_COOKIE_SECURE=os.getenv('SESSION_COOKIE_SECURE', 'True') == 'True',
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        REMEMBER_COOKIE_SECURE=True,
        REMEMBER_COOKIE_HTTPONLY=True,
        REMEMBER_COOKIE_DURATION=86400
    )
def create_app():
    app = Flask(__name__)
    setup_config(app)
    db.init_app(app)
    login_manager.init_app(app)
    csrf = CSRFProtect(app)
    from flask_migrate import Migrate
    Migrate(app, db)
    @app.context_processor
    def inject_globals():
        return {
            'now': datetime.utcnow,
            'csrf_token': generate_csrf()
        }
    from controllers.auth import auth_bp
    from controllers.admin import admin_bp
    from controllers.user import user_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')
    @app.route('/')
    def index():
        if not current_user.is_authenticated:
            return render_template('index.html')
        return redirect(url_for('admin.dashboard' if current_user.is_admin else 'user.dashboard'))
    return app
def init_db(app, check_admin=True):
    with app.app_context():
        db.create_all()
        if check_admin:
            try:
                from models.user import User
                admin = User.query.filter_by(username='admin').first()
                if not admin:
                    admin = User(
                        username='admin',
                        email='admin@parking.com',
                        full_name='Administrator',
                        phone='',
                        is_admin=True
                    )
                    admin.set_password('admin123')
                    db.session.add(admin)
                    db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Skipping admin creation due to: {str(e)}")
            db.session.commit()
            print("Created admin user")
app = create_app()
init_db(app, check_admin=False)
if __name__ == '__main__':
    app.run(debug=True)