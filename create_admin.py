from app import create_app, db
from models.user import User

app = create_app()
with app.app_context():
    admin = User(
        username='MHD',
        email='MHD@example.com',
        is_admin=True
    )
    admin.set_password('123')
    db.session.add(admin)
    db.session.commit()