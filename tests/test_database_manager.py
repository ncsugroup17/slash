import pytest
import sqlite3
from datetime import datetime
from slash.src.modules.DatabaseManager import DatabaseManager
from flask import Flask
from flask.testing import FlaskClient

@pytest.fixture
def db():
    """Fixture to create a fresh in-memory database for testing."""
    db = DatabaseManager(":memory:")  # Use an in-memory database for testing
    yield db
    db.close()


### USER MANAGEMENT TESTS (11) ###
def test_insert_user(db):
    """Test inserting a new user."""
    db.insert_user(email="user@example.com", full_name="John Doe", name="johndoe", password_hash="pass123")
    user = db.get_user("user@example.com")
    assert user is not None
    assert user[1] == "user@example.com"


def test_insert_duplicate_user(db):
    """Test inserting a duplicate user should fail."""
    db.insert_user(email="user@example.com", full_name="John Doe", name="johndoe")
    db.insert_user(email="user@example.com", full_name="Jane Doe", name="janedoe")
    user_count = db.cursor.execute("SELECT COUNT(*) FROM users WHERE email = 'user@example.com'").fetchone()[0]
    assert user_count == 1


def test_user_exists(db):
    """Test checking if a user exists."""
    db.insert_user(email="user@example.com", full_name="John Doe", name="johndoe")
    assert db.user_exists("user@example.com") is True
    assert db.user_exists("unknown@example.com") is False


def test_get_user(db):
    """Test retrieving user details."""
    db.insert_user(email="user@example.com", full_name="John Doe", name="johndoe")
    user = db.get_user("user@example.com")
    assert user is not None
    assert user[2] == "John Doe"


def test_delete_user(db):
    """Test deleting a user."""
    db.insert_user(email="user@example.com", full_name="John Doe", name="johndoe")
    db.delete_user("user@example.com")
    assert db.get_user("user@example.com") is None


def test_update_last_login(db):
    """Test updating last login timestamp and IP."""
    db.insert_user(email="user@example.com", full_name="John Doe", name="johndoe")
    db.update_last_login("user@example.com", last_login_ip="192.168.1.100")
    user = db.get_user("user@example.com")
    assert user[9] is not None  # last_login_at
    assert user[10] == "192.168.1.100"  # last_login_ip


def test_insert_user_with_null_fields(db):
    """Test inserting a user with null optional fields."""
    db.insert_user(email="user@example.com", full_name=None, name=None)
    user = db.get_user("user@example.com")
    assert user is not None


def test_user_deletion_cascades_wishlist(db):
    """Test deleting a user also deletes their wishlist items."""
    db.insert_user(email="user@example.com", full_name="John Doe", name="johndoe")
    db.insert_product("Laptop", "A great laptop", 999.99, "USD", 4.5, 100, "http://example.com", "http://img.com", "Electronics", "amazon")
    db.add_to_wishlist(1, 1)
    db.delete_user("user@example.com")
    wishlist = db.get_wishlist(1)
    assert len(wishlist) == 0


def test_user_deletion_cascades_comments(db):
    """Test deleting a user also deletes their comments."""
    db.insert_user(email="user@example.com", full_name="John Doe", name="johndoe")
    db.insert_product("Laptop", "A great laptop", 999.99, "USD", 4.5, 100, "http://example.com", "http://img.com", "Electronics", "amazon")
    db.add_comment(1, 1, "Nice laptop!", 5)
    db.delete_user("user@example.com")
    comments = db.get_comments(1)
    assert len(comments) == 0


def test_email_verified_default(db):
    """Test if email_verified defaults to 0."""
    db.insert_user(email="user@example.com", full_name="John Doe", name="johndoe")
    user = db.get_user("user@example.com")
    assert user[8] == 0  # email_verified


### PRODUCT MANAGEMENT TESTS (10) ###
def test_insert_product(db):
    """Test inserting a new product."""
    db.insert_product("Laptop", "A great laptop", 999.99, "USD", 4.5, 100, "http://example.com", "http://img.com", "Electronics", "amazon")
    product = db.get_product("http://example.com")
    assert product is not None
    assert product[1] == "Laptop"


def test_insert_duplicate_product(db):
    """Test inserting duplicate product URLs should fail with an IntegrityError."""
    db.insert_product("Laptop", "A great laptop", 999.99, "USD", 4.5, 100, "http://example.com", "http://img.com", "Electronics", "amazon")
    
    with pytest.raises(sqlite3.IntegrityError):  # Expect failure
        db.insert_product("Another Laptop", "Another laptop", 899.99, "USD", 4.0, 50, "http://example.com", "http://img.com", "Electronics", "ebay")

def test_get_product(db):
    """Test retrieving product details."""
    db.insert_product("Laptop", "A great laptop", 999.99, "USD", 4.5, 100, "http://example.com", "http://img.com", "Electronics", "amazon")
    product = db.get_product("http://example.com")
    assert product is not None


def test_product_not_found(db):
    """Test retrieving a non-existent product."""
    product = db.get_product("http://nonexistent.com")
    assert product is None


def test_product_with_null_fields(db):
    """Test inserting a product with null optional fields."""
    db.insert_product("Laptop", None, None, None, None, None, "http://example.com", None, None, "amazon")
    product = db.get_product("http://example.com")
    assert product is not None


def test_product_rating_and_review_defaults(db):
    """Test default values for rating and num_reviews."""
    db.insert_product("Laptop", "A great laptop", 999.99, "USD", None, None, "http://example.com", "http://img.com", "Electronics", "amazon")
    product = db.get_product("http://example.com")
    assert product[5] is None  # rating
    assert product[6] is None  # num_reviews


def test_search_history_empty(db):
    """Test retrieving search history for a non-existent user."""
    history = db.get_search_history(999)
    assert len(history) == 0


def test_get_comments_empty(db):
    """Test retrieving comments for a product with no comments."""
    comments = db.get_comments(999)
    assert len(comments) == 0


def test_wishlist_empty(db):
    """Test retrieving an empty wishlist."""
    wishlist = db.get_wishlist(1)
    assert len(wishlist) == 0


def test_product_source_required(db):
    """Test if product source is required."""
    with pytest.raises(sqlite3.IntegrityError):
        db.cursor.execute("INSERT INTO products (name, url) VALUES ('Laptop', 'http://example.com')")
        db.conn.commit()

def setup_test_data(db):
    user_id = db.add_user("testuser", "test@example.com", "password")
    product_id = db.add_product("Test Product", "Description", 10.0)
    db.connection.commit()  # Ensure data is committed
    return user_id, product_id




def test_wishlist_empty_for_new_user(db):
    """Test that a new user's wishlist is empty."""
    db.insert_user(email="user@example.com", full_name="John Doe", name="johndoe")
    wishlist = db.get_wishlist(1)
    assert len(wishlist) == 0




def test_wishlist_retrieval_non_existent_user(db):
    """Test retrieving wishlist for a non-existent user."""
    wishlist = db.get_wishlist(999)
    assert len(wishlist) == 0

def test_user_wishlist_after_deletion(db):
    """Test that a user's wishlist is deleted after the user is deleted."""
    db.insert_user(email="user@example.com", full_name="John Doe", name="johndoe")
    db.insert_product("Laptop", "A great laptop", 999.99, "USD", 4.5, 100, "http://example.com", "http://img.com", "Electronics", "amazon")
    db.add_to_wishlist(1, 1)
    db.delete_user("user@example.com")
    wishlist = db.get_wishlist(1)
    assert len(wishlist) == 0

# Test adding a product to wishlist without a product
def test_add_product_to_wishlist_without_product(db):
    user_id = 1
    with pytest.raises(sqlite3.IntegrityError):
        db.add_to_wishlist(user_id, None)

# Test adding a product to wishlist with a null user
def test_add_product_to_wishlist_with_null_user(db):
    with pytest.raises(sqlite3.IntegrityError):
        db.add_to_wishlist(None, 1)

# Test adding a product to wishlist with a null product
def test_add_product_to_wishlist_with_null_product(db):
    with pytest.raises(sqlite3.IntegrityError):
        db.add_to_wishlist(1, None)

# Test adding a product to wishlist with an invalid product ID
def test_add_product_to_wishlist_with_invalid_product_id(db):
    user_id = 1
    invalid_product_id = 9999
    with pytest.raises(sqlite3.IntegrityError):
        db.add_to_wishlist(user_id, invalid_product_id)

# Test adding a product to wishlist with an invalid user ID
def test_add_product_to_wishlist_with_invalid_user_id(db):
    invalid_user_id = 9999
    product_id = 1
    with pytest.raises(sqlite3.IntegrityError):
        db.add_to_wishlist(invalid_user_id, product_id)

def test_add_product_to_wishlist_with_existing_product(db):
    """Test adding an already existing product to the wishlist."""
    db.insert_user(email="user@example.com", full_name="John Doe", name="johndoe")
    db.insert_product("Laptop", "A great laptop", 999.99, "USD", 4.5, 100, "http://example.com", "http://img.com", "Electronics", "amazon")
    db.add_to_wishlist(1, 1)
    wishlist = db.get_wishlist(1)
    assert len(wishlist) == 1

def test_retrieve_wishlist_with_multiple_products(db):
    """Test retrieving wishlist for a user with multiple products."""
    db.insert_user(email="user@example.com", full_name="John Doe", name="johndoe")
    db.insert_product("Laptop", "A great laptop", 999.99, "USD", 4.5, 100, "http://example.com", "http://img.com", "Electronics", "amazon")
    db.insert_product("Phone", "A great phone", 499.99, "USD", 4.0, 50, "http://example.com/phone", "http://img.com/phone", "Electronics", "amazon")
    db.add_to_wishlist(1, 1)
    db.add_to_wishlist(1, 2)
    wishlist = db.get_wishlist(1)
    assert len(wishlist) == 2


### COMMENT MANAGEMENT TESTS (10) ###

def add_comment(self, user_id, product_id, comment, rating):
    if comment is None:
        comment = ""  # Ensure comment is never None
    self.cursor.execute("""
        INSERT INTO comments (user_id, product_id, comment, rating)
        VALUES (?, ?, ?, ?)
    """, (user_id, product_id, comment, rating))
    self.conn.commit()

def test_add_multiple_comments(db):
    """Test adding multiple comments for the same product."""
    db.insert_user(email="user1@example.com", full_name="John Doe", name="johndoe")
    db.insert_user(email="user2@example.com", full_name="Jane Doe", name="janedoe")
    db.insert_product("Laptop", "A great laptop", 999.99, "USD", 4.5, 100, "http://example.com", "http://img.com", "Electronics", "amazon")
    
    # Ensure both users exist before adding comments
    db.add_comment(1, 1, "Great laptop!", 5)
    db.add_comment(2, 1, "Not bad", 4)
    
    comments = db.get_comments(1)
    assert len(comments) == 2

def test_comment_not_found(db):
    """Test retrieving comments for a non-existent product."""
    comments = db.get_comments(999)
    assert len(comments) == 0

def update_comment(self, user_id, product_id, new_comment, new_rating):
    self.cursor.execute("""
        UPDATE comments
        SET comment = ?, rating = ?
        WHERE user_id = ? AND product_id = ?
    """, (new_comment, new_rating, user_id, product_id))
    self.conn.commit()

def delete_comment(self, user_id, product_id):
    self.cursor.execute("""
        DELETE FROM comments
        WHERE user_id = ? AND product_id = ?
    """, (user_id, product_id))
    self.conn.commit()

def test_add_comment_with_invalid_user(db):
    """Test adding a comment with an invalid user."""
    invalid_user_id = 9999
    with pytest.raises(sqlite3.IntegrityError):
        db.add_comment(invalid_user_id, 1, "Invalid user comment", 5)

def test_add_comment_with_invalid_product(db):
    """Test adding a comment to a non-existent product."""
    db.insert_user(email="user@example.com", full_name="John Doe", name="johndoe")
    invalid_product_id = 9999
    with pytest.raises(sqlite3.IntegrityError):
        db.add_comment(1, invalid_product_id, "Invalid product comment", 5)


def get_comments(self, product_id):
    self.cursor.execute("""
        SELECT user_id, product_id, comment, rating, created_at
        FROM comments
        WHERE product_id = ?
    """, (product_id,))
    return self.cursor.fetchall()

