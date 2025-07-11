from app import create_app, db
from models.user import User
from werkzeug.security import generate_password_hash

app = create_app()

def reset_demo_passwords():
    """
    Reset all users to have the password '123' stored as plaintext.
    This is only for demonstration purposes - never do this in a real application!
    """
    with app.app_context():
        users = User.query.all()
        
        print(f"Found {len(users)} users in database")
        print("User IDs and usernames:", [(user.id, user.username) for user in users])
        
        for user in users:
            print(f"Before: User {user.username} has password_hash: {user.password_hash}")
            # Set all passwords to '123' for simplicity
            user.password_hash = '123'
            print(f"After: User {user.username} has password_hash: {user.password_hash}")
        
        db.session.commit()
        print(f"Successfully reset {len(users)} user passwords to plaintext")

if __name__ == "__main__":
    reset_demo_passwords()
