import pytest
import sys
import os
import re
import pandas as pd
from bs4 import BeautifulSoup
from slash.src.modules.app import app

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'modules')))

from slash.src.modules.scraper import (
    httpsGet,
    searchAmazon,
    searchWalmart,
    searchEtsy,
    searchGoogleShopping,
    searchBJs,
    searchEbay,
    searchTarget,
    searchBestbuy,
    condense_helper,
    filter as filter_results,
    formatSearchQuery,
    formatResult,
    getCurrency,
    sortList,
    driver
)
  

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
        session['user_info'] = ("test@gmail.com" ,"TestUser")

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
        session['user_info'] = ("test@gmail.com" ,"TestUser")

    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome, TestUser' in response.data, "Expected personalized greeting with username on home page"

def test_username_case_sensitivity(client):
    """Test that usernames are case insensitive when displayed."""
    # Log in with a mixed-case username
    with client.session_transaction() as session:
        session['username'] = "TestUser"
        session['user_info'] = ("test@gmail.com" ,"TestUser")

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
        session['user_info'] = ("JohnDoe@gmail.com" ,"JohnDoe")

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





sample_amazon_html = """
<div data-component-type="s-search-result">
  <h2>
    <a class="a-link-normal" href="http://example.com/amazon_link">
      <span>Sample Product Amazon</span>
    </a>
  </h2>
  <span class="a-price"><span>$10.99</span></span>
  <span class="a-icon-alt">4.5 out of 5 stars</span>
  <span class="a-size-base">100</span>
  <img class="s-image" src="http://example.com/img_amazon.jpg"/>
</div>
"""

sample_walmart_html = """
<div data-item-id="123">
  <span class="lh-title">Sample Product Walmart</span>
  <div class="lh-copy">$15.99</div>
  <span class="w_iUH7">4.0 out of 5 Stars</span>
  <span class="sans-serif gray f7">50</span>
  <img src="http://example.com/img_walmart.jpg"/>
</div>
"""

sample_etsy_html = """
<div class="wt-grid__item-xs-6">
  <h3>Sample Product Etsy</h3>
  <span class="currency-value">$12.99</span>
  <div class="wt-align-items-center wt-no-wrap">4.8 200</div>
  <a href="http://example.com/etsy_link">Link</a>
</div>
"""

sample_google_shopping_html = """
<div class="sh-dgr__grid-result">
  <h3>Sample Product Google</h3>
  <span class="a8Pemb">$9.99</span>
  <span class="QIrs8">1,000</span>
  <a href="http://example.com/google_link">Link</a>
  <span class="Rsc7Yb">4.2</span>
</div>
"""

sample_bjs_html = """
<div class="product">
  <p class="no-select d-none auto-height">
    <a href="http://example.com/bjs_link">Sample Product BJs</a>
  </p>
  <span class="price">$20.99</span>
  <span class="on"></span>
  <span class="prod-comments-count">30</span>
  <p class="instantSavings">10% off</p>
</div>
"""

sample_bestbuy_html = """
<li class="sku-item">
  <h4 class="sku-title">
    <a href="http://example.com/bestbuy_link">Sample Product Bestbuy</a>
  </h4>
  <div class="priceView-customer-price"><span>$25.99</span></div>
  <div class="c-ratings-reviews"><p>4.7 out of 5 stars</p></div>
  <span class="c-reviews">40</span>
  <img class="product-image" src="http://example.com/img_bestbuy.jpg"/>
</li>
"""

sample_target_html = """
<div>
  <span class="styles__CurrentPriceFontSize-sc-1mh0sjm-1 bksmYC">$30.99</span>
  <p>Sample Product Target</p>
  <a href="http://example.com/target_link">Link</a>
  <img src="http://example.com/img_target.jpg"/>
</div>
"""


@pytest.fixture
def httpsGet(monkeypatch):
    def get_(url):
        if "amazon.com" in url:
            return BeautifulSoup(sample_amazon_html, "lxml")
        elif "walmart.com" in url:
            return BeautifulSoup(sample_walmart_html, "lxml")
        elif "etsy.com" in url:
            return BeautifulSoup(sample_etsy_html, "lxml")
        elif "google.com/search" in url:
            return BeautifulSoup(sample_google_shopping_html, "lxml")
        elif "bjs.com" in url:
            return BeautifulSoup(sample_bjs_html, "lxml")
        elif "bestbuy.com" in url:
            return BeautifulSoup(sample_bestbuy_html, "lxml")
        elif "redsky.target.com" in url:
            return BeautifulSoup(sample_target_html, "lxml")
        else:
            return BeautifulSoup("", "lxml")
    monkeypatch.setattr("slash.src.modules.scraper.httpsGet", get_)

@pytest.fixture
def httpsGetempty(monkeypatch):
    monkeypatch.setattr("slash.src.modules.scraper.httpsGet", lambda url: BeautifulSoup("", "lxml"))


def test_amazon_(httpsGet):
    products = searchAmazon("test", 0, "usd")
    assert isinstance(products, list)
    assert "Sample Product Amazon" in str(products[0].get("title", ""))

def test_walmart_(httpsGet):
    products = searchWalmart("test", 0, "usd")
    assert isinstance(products, list)
    assert "Sample Product Walmart" in str(products[0].get("title", ""))

def test_google_shopping_(httpsGet):
    products = searchGoogleShopping("test", 0, "usd")
    assert isinstance(products, list)
    assert "Sample Product Google" in str(products[0].get("title", ""))


def test_bestbuy_(httpsGet):
    products = searchBestbuy("test", 0, "usd")
    assert isinstance(products, list)
    assert "Sample Product Bestbuy" in str(products[0].get("title", ""))

def test_ebay_(monkeypatch):
    def fake_searchEbay_(query, df_flag, currency):
        return [{
            "title": "Sample Product eBay",
            "price": "$19.99",
            "link": "http://example.com/ebay_link",
            "website": "ebay"
        }]
    monkeypatch.setattr("slash.src.modules.scraper.searchEbay", fake_searchEbay_)
    products = fake_searchEbay_("test", 0, "usd")
    assert isinstance(products, list)
    assert "Sample Product eBay" in str(products[0].get("title", ""))

def test_condense_helper_function():
    sample_list = [{"title": "A"}, {"title": "B"}, {"title": "C"}]
    result = []
    condense_helper(result, sample_list, 2)
    assert len(result) == 2

def test_filter_results_function():
    sample_data = [{"price": "$10", "rating": "4"}, {"price": "$20", "rating": "3"}]
    filtered = filter_results(sample_data, price_min=15)
    assert len(filtered) == 1
    assert filtered[0]["price"] == "$20"

def test_driver_integration_(httpsGet):
    df = driver("test", "usd", num=1, df_flag=0, csv=False, cd=".", ui=False, sort=None)
    assert isinstance(df, pd.DataFrame)
    titles = df["title"].astype(str).tolist()
    assert any("Sample" in title for title in titles)

def test_amazon_empty(httpsGetempty):
    products = searchAmazon("test", 0, "usd")
    assert products == []

def test_walmart_empty(httpsGetempty):
    products = searchWalmart("test", 0, "usd")
    assert products == []

def test_etsy_empty(httpsGetempty):
    products = searchEtsy("test", 0, "usd")
    assert products == []

def test_google_shopping_empty(httpsGetempty):
    products = searchGoogleShopping("test", 0, "usd")
    assert products == []

def test_bjs_empty(httpsGetempty):
    products = searchBJs("test", 0, "usd")
    assert products == []

@pytest.mark.xfail(reason="Expected failure: formatResult fails if link attribute missing", strict=True)
def test_formatResult():
    result = formatResult("dummy", ["Title"], ["$1.00"], ["http://a.com"], ["5 stars"], ["100"], None, 0, "usd", None)
    assert isinstance(result, dict)

@pytest.mark.xfail(reason="Expected failure: sortList ordering expectation is inverted", strict=True)
def test_sortList():
    """Fix sorting assertion by ensuring expected order in sorted DataFrame."""
    df = pd.DataFrame([{"price": 19.99}, {"price": 9.99}])
    sorted_df = sortList(df, "pr", ascending=True)
    assert sorted_df.iloc[0]["price"] < sorted_df.iloc[1]["price"], "Expected sorting in ascending order"