import os
import sys
from app import create_app, db
from app.core.models import User
from getpass import getpass

def create_admin_user(username, password):
    """Create an admin user if it doesn't exist"""
    app = create_app()
    
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"User '{username}' already exists.")
            return False
        
        # Create new user
        user = User(username=username, role='admin')
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            print(f"Admin user '{username}' created successfully.")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error creating user: {e}")
            return False

if __name__ == '__main__':
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = input("Enter admin username: ")
        
    password = getpass("Enter admin password: ")
    confirm_password = getpass("Confirm password: ")
    
    if password != confirm_password:
        print("Passwords don't match!")
        sys.exit(1)
        
    if len(password) < 6:
        print("Password too short! Minimum 6 characters required.")
        sys.exit(1)
        
    create_admin_user(username, password) 