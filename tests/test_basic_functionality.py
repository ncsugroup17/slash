import unittest
import sys
import os
import re
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from slash.src.modules.features import find_currency, usr_dir
from slash.src.modules.formatter import formatSearchQuery

def filter_results(data, price_min=None, price_max=None, rating_min=None):
    """Filter products based on price and rating."""
    filtered_result = []
    
    for product in data:
        price_str = product.get("price", "")
        rating_str = product.get("rating", "")
        
        if not price_str or not rating_str:
            continue
            
        price_num = float(re.sub(r'[^\d.]', '', price_str))
        
        try:
            rating_num = float(rating_str)
        except (ValueError, TypeError):
            rating_num = 0
            
        price_min_check = price_min is None or price_num >= price_min
        price_max_check = price_max is None or price_num <= price_max
        rating_check = rating_min is None or rating_num >= rating_min
        
        if price_min_check and price_max_check and rating_check:
            filtered_result.append(product)
            
    return filtered_result

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    from slash.src.modules.app import app
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client

class TestBasicFunctionality:
    """Basic tests that don't rely on external dependencies."""
    
    def test_formatSearchQuery(self):
        """Test that formatSearchQuery correctly formats search strings."""
        assert formatSearchQuery("laptop") == "laptop"
        assert formatSearchQuery("apple macbook") == "apple+macbook"
        assert formatSearchQuery("t shirt") == "t+shirt"
        
    def test_find_currency(self):
        """Test that find_currency extracts currency codes correctly."""
        assert find_currency("USD100.00") == "USD"
        assert find_currency("EUR50") == "EUR"
        assert find_currency("GBP75.99") == "GBP"
        assert find_currency("$100.00") is None
        
    def test_filter_by_price_min(self):
        """Test filtering products by minimum price."""
        products = [
            {"price": "$20.00", "rating": "4.5"},
            {"price": "$50.00", "rating": "4.0"},
            {"price": "$100.00", "rating": "4.8"}
        ]
        
        result = filter_results(products, price_min=30)
        assert len(result) == 2
        assert products[1] in result
        assert products[2] in result
        
    def test_filter_by_price_max(self):
        """Test filtering products by maximum price."""
        products = [
            {"price": "$20.00", "rating": "4.5"},
            {"price": "$50.00", "rating": "4.0"},
            {"price": "$100.00", "rating": "4.8"}
        ]
        
        result = filter_results(products, price_max=60)
        assert len(result) == 2
        assert products[0] in result
        assert products[1] in result
        
    def test_filter_by_rating(self):
        """Test filtering products by minimum rating."""
        products = [
            {"price": "$20.00", "rating": "3.5"},
            {"price": "$50.00", "rating": "4.0"},
            {"price": "$100.00", "rating": "4.8"}
        ]
        
        result = filter_results(products, rating_min=4.0)
        assert len(result) == 2
        assert products[1] in result
        assert products[2] in result
        
    def test_filter_combined(self):
        """Test filtering products by price and rating."""
        products = [
            {"price": "$20.00", "rating": "3.5"},
            {"price": "$50.00", "rating": "4.0"},
            {"price": "$100.00", "rating": "4.8"},
            {"price": "$30.00", "rating": "4.2"}
        ]
        
        result = filter_results(products, price_min=25, price_max=75, rating_min=4.0)
        assert len(result) == 2
        assert products[1] in result
        assert products[3] in result
    
    def test_usr_dir_returns_correct_path(self):
        """Test that usr_dir returns the correct path for a user."""
        from slash.src.modules.features import users_main_dir
        email = "test@example.com"
        expected_path = os.path.join(users_main_dir, email)
        assert str(usr_dir(email)) == str(expected_path)
        
    def test_filter_empty_input(self):
        """Test filtering with empty input data."""
        products = []
        result = filter_results(products, price_min=10, price_max=100, rating_min=4.0)
        assert len(result) == 0
        assert isinstance(result, list)
        
    def test_filter_with_missing_values(self):
        """Test filtering products with missing price or rating values."""
        products = [
            {"title": "Product with no price", "rating": "4.5"},
            {"price": "$50.00", "title": "Product with no rating"},
            {"price": "$30.00", "rating": "4.2", "title": "Complete product"}
        ]
        
        result = filter_results(products)
        assert len(result) == 1
        assert products[2] in result


class TestAppRoutes:
    """Tests for Flask routes with minimal dependencies."""
    
    def test_landing_page(self, client):
        """Test that landing page route returns 200."""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_login_page(self, client):
        """Test that login page route returns 200."""
        response = client.get('/login')
        assert response.status_code == 200
    
    def test_register_page(self, client):
        """Test that register page route returns 200."""
        response = client.get('/register')
        assert response.status_code == 200
    
    def test_logout_redirects(self, client):
        """Test that logout redirects."""
        response = client.get('/logout', follow_redirects=False)
        assert response.status_code == 302
    
    @patch('slash.src.modules.app.check_user')
    def test_login_with_valid_credentials(self, mock_check_user, client):
        """Test login with valid credentials."""
        mock_check_user.return_value = True
        
        with patch('slash.src.modules.app.render_template') as mock_render:
            mock_render.return_value = "Successful login"
            
            response = client.post('/login', data={
                'username': 'test@example.com',
                'password': 'password123'
            }, follow_redirects=False)
            
            assert response.status_code == 302
            
            with client.session_transaction() as session:
                assert session['username'] == 'test@example.com'
    
    @patch('slash.src.modules.app.check_user')
    def test_login_with_invalid_credentials(self, mock_check_user, client):
        """Test login with invalid credentials."""
        mock_check_user.return_value = False
        
        with patch('slash.src.modules.app.render_template') as mock_render:
            mock_render.return_value = "Login page with invalid=True"
            
            response = client.post('/login', data={
                'username': 'wrong@example.com',
                'password': 'wrongpassword'
            })
            
            mock_render.assert_called_once()
            call_args = mock_render.call_args[1]
            assert call_args.get('invalid') is True
    
    @patch('slash.src.modules.app.create_user')
    def test_register_new_user(self, mock_create_user, client):
        """Test registering a new user."""
        mock_create_user.return_value = True
        
        response = client.post('/register', data={
            'username': 'newuser@example.com',
            'password': 'newpassword123'
        }, follow_redirects=False)
        
        assert response.status_code == 302 
        assert '/login' in response.headers['Location']
    
    def test_logout_clears_session(self, client):
        """Test that logout clears the session data."""
        with client.session_transaction() as session:
            session['username'] = 'test@example.com'
        
        client.get('/logout')
        
        with client.session_transaction() as session:
            assert 'username' not in session
    
    @patch('slash.src.modules.app.driver')
    def test_search_redirects_when_not_logged_in(self, mock_driver, client):
        """Test that search redirects to login when user is not logged in."""
        response = client.get('/search', query_string={'product_name': 'laptop'})
        
        assert response.status_code == 302
        assert '/login' in response.headers['Location']
        mock_driver.assert_not_called()
    
    @patch('slash.src.modules.app.driver')
    def test_search_with_empty_query(self, mock_driver, client):
        """Test search with empty query."""
        with client.session_transaction() as session:
            session['username'] = 'test@example.com'
            session['user_info'] = ('test@example.com', 'TestUser')
            
        with patch('slash.src.modules.app.render_template') as mock_render:
            mock_render.return_value = "Search results page with error message"
            
            response = client.get('/search', query_string={'product_name': ''})
            
            mock_render.assert_called_once()
            call_args = mock_render.call_args[1]  # Get keyword arguments
            assert "Please enter a search term" in call_args.get('error', '')
            
            mock_driver.assert_not_called()
            
    @patch('slash.src.modules.app.create_user')
    def test_register_failed_user_creation(self, mock_create_user, client):
        """Test registering a user when creation fails."""
        mock_create_user.return_value = False
        
        with patch('slash.src.modules.app.render_template') as mock_render:
            mock_render.return_value = "Registration failed page"
            
            response = client.post('/register', data={
                'username': 'existing@example.com',
                'password': 'password123'
            })
            
            mock_render.assert_called_once()
            call_args = mock_render.call_args[1]
            assert call_args.get('login') is False
            assert call_args.get('invalid') is True


if __name__ == '__main__':
    unittest.main() 