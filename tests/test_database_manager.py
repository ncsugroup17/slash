import pytest
import sqlite3
from datetime import datetime
from slash.src.modules.DatabaseManager import DatabaseManager

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
