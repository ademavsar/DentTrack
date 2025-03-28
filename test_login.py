"""
Test script to check Flask-Login session handling
Run this script with: python test_login.py
"""
from app import create_app
from flask import session
from flask_login import current_user, login_user, logout_user
from app.core.models import User

# Create a Flask application instance with debug config
app = create_app({
    'TESTING': True,
    'DEBUG': True,
    'SECRET_KEY': 'testing-key'
})

def test_login_flow():
    """Test login flow and session handling"""
    with app.app_context():
        with app.test_client() as client:
            # Make a request to root
            print("\n---- First request to / (should redirect to login) ----")
            response = client.get('/')
            print(f"Status code: {response.status_code}")
            print(f"Redirected: {response.status_code == 302}")
            if response.status_code == 302:
                print(f"Location: {response.headers.get('Location')}")
            
            # Try to log in a user manually
            print("\n---- Trying to log in user ----")
            user = User.query.filter_by(username='admin').first()
            if not user:
                print("No admin user found!")
            else:
                print(f"Found user: {user}")
                
                # Log in via the login form
                print("\n---- Using login form to authenticate ----")
                login_response = client.post('/auth/login', data={
                    'username': 'admin',
                    'password': 'admin123',  # assuming this is the password
                    'remember_me': True
                }, follow_redirects=False)
                
                print(f"Login response status: {login_response.status_code}")
                print(f"Login redirected: {login_response.status_code == 302}")
                if login_response.status_code == 302:
                    print(f"Login redirect location: {login_response.headers.get('Location')}")
                
                # Get the session and cookies
                print("\n---- Session cookies ----")
                print(f"Session after login: {session.items() if '_user_id' in session else 'No user in session'}")
                
                # Make another request to root after login
                print("\n---- Request to / after login ----")
                home_response = client.get('/')
                print(f"Home status code: {home_response.status_code}")
                print(f"Redirected: {home_response.status_code == 302}")
                if home_response.status_code == 302:
                    print(f"Redirect location: {home_response.headers.get('Location')}")
                
                # Check the test authentication endpoint
                print("\n---- Test authentication endpoint ----")
                auth_test_response = client.get('/auth/test-auth')
                print(f"Auth test response: {auth_test_response.data.decode('utf-8')}")

if __name__ == "__main__":
    test_login_flow() 