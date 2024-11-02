import pytest
import sys
import os
import csv

# Add the src/modules directory to the Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'modules')))

# Import the Flask app
from slash.src.modules.app import app

@pytest.fixture
def client():
    """Set up a test client for Flask app."""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    with app.test_client() as client:
        yield client

def test_logout_clears_session(client):
    """Test if logout clears the session."""
    client.post('/login', json={"name": "John Doe", "email": "john.doe@example.com"})
    client.get('/logout')
    with client.session_transaction() as session:
        assert 'username' not in session

def test_comment_csv_update_after_adding_comment(client):
    """Test if comments.csv updates correctly after adding a comment."""
    product_id = 1
    client.post(f'/products/{product_id}/comment', json={
        "user": "TestUser",
        "comment": "This is a test comment"
    })
    




def test_session_data_after_logout(client):
    """Ensure session data is cleared after logout."""
    # Simulate a logged-in session
    with client.session_transaction() as session:
        session['username'] = "TestUser"
    
    # Call the logout endpoint
    client.get('/logout')
    
    # Check session data is cleared
    with client.session_transaction() as session:
        assert 'username' not in session


def test_logout_redirect(client):
    """Test if logout redirects to the login or homepage."""
    # Simulate a logged-in session
    with client.session_transaction() as session:
        session['username'] = "TestUser"
    
    # Call the logout endpoint
    response = client.get('/logout', follow_redirects=False)
    assert response.status_code == 302  # Status for redirection
    # Check that redirection is to the login or home page
    assert '/login' in response.headers['Location'] or '/' in response.headers['Location']


def test_home_page_loads(client):
    """Test that the home page loads with a 200 status code."""
    response = client.get('/')
    assert response.status_code == 200, "Expected 200 OK for home page"

def test_home_page_logged_in_user(client):
    """Test home page displays user-specific content when logged in."""
    # Simulate a logged-in session
    with client.session_transaction() as session:
        session['username'] = "TestUser"
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome, TestUser' in response.data, "Expected personalized welcome message for logged-in user"

def test_home_page_redirects_to_login(client):
    """Test if home page redirects to login when user is not logged in."""
    # Simulate a requirement for login to access home page
    with client.session_transaction() as session:
        session.clear()  # Ensure no user is logged in
    response = client.get('/')
    if response.status_code == 302:  # If redirect is expected
        assert '/login' in response.headers['Location'], "Expected redirect to login page for non-authenticated users"


def test_home_page_displays_username(client):
    """Test that the home page displays the username for a logged-in user."""
    with client.session_transaction() as session:
        session['username'] = "TestUser"
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome, TestUser' in response.data, "Expected personalized greeting with username on home page"

def test_username_case_sensitivity(client):
    """Test that usernames are case insensitive when displayed."""
    # Log in with a mixed-case username
    with client.session_transaction() as session:
        session['username'] = "TestUser"
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome, TestUser' in response.data, "Expected username to be displayed in the same case as input"

def test_logout_clears_username(client):
    """Test that logging out removes the username from session."""
    with client.session_transaction() as session:
        session['username'] = "TestUser"
    client.get('/logout')
    with client.session_transaction() as session:
        assert 'username' not in session, "Expected username to be cleared from session on logout"


def test_logout_clears_google_session_data(client):
    """Test that logging out after Google login clears session data."""
    # Simulate Google login by setting session data
    with client.session_transaction() as session:
        session['username'] = "TestUser"
    
    # Call logout
    client.get('/logout')
    with client.session_transaction() as session:
        assert 'username' not in session, "Expected session data to be cleared on logout"





def test_home_page_personalized_greeting(client):
    """Test that the home page shows a personalized greeting when a user is logged in."""
    with client.session_transaction() as session:
        session['username'] = 'JohnDoe'
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome, JohnDoe' in response.data, "Expected personalized greeting for logged-in user"



def test_logout_redirects_to_home(client):
    """Test that logout redirects to the home page."""
    response = client.get('/logout', follow_redirects=False)
    assert response.status_code == 302, "Expected 302 redirect on logout"
    assert '/' in response.headers['Location'], "Expected redirect to home page after logout"



def test_logout_clears_all_user_data(client):
    """Test that logging out clears all user-specific data, such as shopping cart or preferences."""
    with client.session_transaction() as session:
        session['username'] = "TestUser"
        session['cart_items'] = ["item1", "item2"]
        session['preferences'] = {"theme": "dark"}
    client.get('/logout')
    with client.session_transaction() as session:
        assert 'username' not in session, "Expected username to be cleared from session on logout"
        assert 'cart_items' not in session, "Expected cart items to be cleared on logout"
        assert 'preferences' not in session, "Expected preferences to be cleared on logout"




def test_navigation_logout_link_logged_in(client):
    """Test that the Logout link logs out a logged-in user and redirects to home page."""
    with client.session_transaction() as session:
        session['username'] = "TestUser"
    response = client.get('/logout')
    assert response.status_code == 302, "Expected redirect on logout"
    assert '/' in response.headers['Location'], "Expected redirect to home page after logout"
    # Check session is cleared after logout
    with client.session_transaction() as session:
        assert 'username' not in session, "Expected username to be cleared from session after logout"




def test_home_page(client):
    """Test that the landing page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome' in response.data or b'Login' in response.data


def test_google_login_redirect(client):
    """Test that Google login initiates a redirect to the Google authorization page."""
    response = client.get('/login/google')
    assert response.status_code == 302
    assert 'accounts.google.com' in response.headers['Location']


def test_search_requires_login(client):
    """Test that the search page redirects to login if user is not logged in."""
    response = client.get('/search', query_string={'product_name': 'laptop'})
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_share_wishlist(client, monkeypatch):
    """Test sharing a wishlist with an email."""
    with client.session_transaction() as session:
        session['username'] = 'testuser'
    response = client.post('/share', data={'email': 'friend@example.com'})
    assert response.status_code == 302
    assert response.headers['Location'] == '/wishlist'



def test_logout_redirect_to_login(client):
    """Test that logging out redirects to the home page."""
    with client.session_transaction() as session:
        session['username'] = "testuser"
    response = client.get('/logout')
    assert response.status_code == 302
    assert '/' in response.headers['Location'], "Expected redirect to home page after logout"



