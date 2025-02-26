import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_file="database.db"):
        """Initialize the database connection."""
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")

        self.create_tables()

    def create_tables(self):
        """Creates all necessary tables if they don't exist."""
        sql_script = """
        -- Users Table
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT DEFAULT NULL,
            name TEXT DEFAULT NULL,
            password_hash TEXT DEFAULT NULL,
            phone_number TEXT DEFAULT NULL,
            dob DATE DEFAULT NULL,
            address TEXT DEFAULT NULL,
            email_verified BOOLEAN DEFAULT 0,
            last_login_at DATETIME DEFAULT NULL,
            last_login_ip TEXT CHECK (last_login_ip GLOB '[0-9a-fA-F:.]*') DEFAULT NULL,
            account_status TEXT CHECK (account_status IN ('active', 'banned', 'suspended')) DEFAULT 'active',
            role TEXT DEFAULT 'user',
            profile_picture_url TEXT DEFAULT NULL,
            two_factor_enabled BOOLEAN DEFAULT 0,
            last_activity_at DATETIME DEFAULT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- Products Table
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT DEFAULT NULL,
            price REAL DEFAULT NULL,
            currency TEXT DEFAULT NULL,
            rating REAL DEFAULT NULL,
            num_reviews INTEGER DEFAULT NULL,
            url TEXT UNIQUE NOT NULL,
            image_url TEXT DEFAULT NULL,
            category TEXT DEFAULT NULL,
            source TEXT NOT NULL,
            last_scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- Search History Table
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            search_query TEXT NOT NULL,
            filters_applied TEXT DEFAULT NULL,
            num_results INTEGER DEFAULT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        -- Wishlists Table
        CREATE TABLE IF NOT EXISTS wishlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            added_on DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        );

        -- Comments Table
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            comment TEXT NOT NULL,
            rating_given REAL DEFAULT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        );
        """
        self.cursor.executescript(sql_script)
        self.conn.commit()

    ### USER MANAGEMENT ###
    def insert_user(self, email, full_name, name, password_hash=None, phone_number=None, dob=None, address=None, 
                email_verified=False, profile_picture_url=None, google_id=None):
        """Inserts a new user into the database, supporting Google OAuth users."""
        try:
            self.cursor.execute("""
                INSERT INTO users (email, full_name, name, password_hash, phone_number, dob, address, 
                                email_verified, profile_picture_url, last_login_at, last_activity_at, created_at, account_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (email, full_name, name, password_hash, phone_number, dob, address, 
                int(email_verified), profile_picture_url, datetime.now(), datetime.now(), datetime.now(), "active"))
            self.conn.commit()
        except sqlite3.IntegrityError:
            print(f"User with email {email} already exists!")

    def update_last_login(self, email, last_login_ip=None):
        """Updates the last login time and IP for a user."""
        self.cursor.execute("""
            UPDATE users 
            SET last_login_at = ?, last_login_ip = ?, last_activity_at = ? 
            WHERE email = ?
        """, (datetime.now(), last_login_ip, datetime.now(), email))
        self.conn.commit()


    def user_exists(self, email):
        """Checks if a user exists in the database by email."""
        self.cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", (email,))
        result = self.cursor.fetchone()
        return result[0] > 0  # Returns True if user exists, False otherwise
    
    def get_user(self, email):
        """Retrieves user details by email."""
        self.cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        return self.cursor.fetchone()

    def delete_user(self, email):
        """Deletes a user by email."""
        self.cursor.execute("DELETE FROM users WHERE email = ?", (email,))
        self.conn.commit()

    ### PRODUCT MANAGEMENT ###
    def insert_product(self, name, description, price, currency, rating, num_reviews, url, image_url, category, source):
        """Inserts a new product into the database."""
        self.cursor.execute("""
            INSERT INTO products (name, description, price, currency, rating, num_reviews, url, image_url, category, source, last_scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, description, price, currency, rating, num_reviews, url, image_url, category, source, datetime.now()))
        self.conn.commit()

    def get_product(self, url):
        """Retrieves product details by URL."""
        self.cursor.execute("SELECT * FROM products WHERE url = ?", (url,))
        return self.cursor.fetchone()

    ### SEARCH HISTORY ###
    def log_search(self, user_id, search_query, filters_applied=None, num_results=None):
        """Logs a user's search query."""
        self.cursor.execute("""
            INSERT INTO search_history (user_id, search_query, filters_applied, num_results, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, search_query, filters_applied, num_results, datetime.now()))
        self.conn.commit()

    def get_search_history(self, user_id):
        """Retrieves search history for a user."""
        self.cursor.execute("SELECT * FROM search_history WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
        return self.cursor.fetchall()

   ### WISHLIST MANAGEMENT ###
    def get_wishlist(self, user_id):
        """Retrieves all products in a user's wishlist."""
        self.cursor.execute("""
            SELECT p.* FROM products p
            INNER JOIN wishlists w ON p.id = w.product_id
            WHERE w.user_id = ?
        """, (user_id,))
        return self.cursor.fetchall()
    
    def is_product_in_wishlist(self, user_id, product_id):
        self.cursor.execute('''
            SELECT 1 FROM wishlists WHERE user_id = ? AND product_id = ?
        ''',    (user_id, product_id))
        return self.cursor.fetchone() is not None

    # def add_to_wishlist(self, user_id, title, image, price, website, rating):
    #     self.cursor.execute('''
    #         INSERT INTO wishlist (user_id, title, image, price, website, rating)
    #         VALUES (?, ?, ?, ?, ?, ?)
    #     ''', (user_id, title, image, price, website, rating))
    #     self.conn.commit()

    def remove_from_wishlist(self, user_id, product_id):
        self.cursor.execute('''
            DELETE FROM wishlists WHERE user_id = ? AND id = ?
        ''', (user_id, product_id))
        self.conn.commit()

    def add_to_wishlist(self, user_id, product_id):
        """Adds a product to the user's wishlists, preventing duplicates."""
        self.cursor.execute("""
            SELECT 1 FROM wishlists WHERE user_id = ? AND product_id = ?
        """, (user_id, product_id))
        
        if self.cursor.fetchone():
            return  # Product is already in the wishlist, do nothing

        self.cursor.execute("""
            INSERT INTO wishlists (user_id, product_id, added_on)
            VALUES (?, ?, ?)
        """, (user_id, product_id, datetime.now()))
        self.conn.commit()


    ### COMMENTS MANAGEMENT ###
    def add_comment(self, user_id, product_id, comment, rating_given=None):
        """Adds a comment to a product."""
        self.cursor.execute("""
            INSERT INTO comments (user_id, product_id, comment, rating_given, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, product_id, comment, rating_given, datetime.now()))
        self.conn.commit()

    def get_comments(self, product_id):
        """Retrieves all comments for a product."""
        self.cursor.execute("""
            SELECT u.name, c.comment, c.rating_given, c.timestamp
            FROM comments c
            INNER JOIN users u ON c.user_id = u.id
            WHERE c.product_id = ?
            ORDER BY c.timestamp DESC
        """, (product_id,))
        return self.cursor.fetchall()

    def get_user(self, username):
        self.cursor.execute('''
            SELECT id FROM users WHERE email = ?
        ''', (username,))
        return self.cursor.fetchone()

    def close(self):
        """Closes the database connection."""
        self.conn.close()
