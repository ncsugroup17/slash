"""
Copyright (C) 2023 SE23-Team44
Licensed under the MIT License.
See the LICENSE file in the project root for the full license information.
"""
import time
import os
import csv
import sqlite3
from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests
from .scraper import driver
from .features import (
    create_user, check_user, wishlist_add_item,
    read_wishlist, wishlist_remove_list, share_wishlist
)
from .config import Config
from .DatabaseManager import DatabaseManager

# Initialize Flask app
app = Flask(__name__, template_folder=".")
app.secret_key = Config.SECRET_KEY
db = DatabaseManager()

wishlist = []

# Google OAuth2 setup (Use secure transport in production)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(__file__), "..", "client_secret_92320207172-8cnk4c9unfaa7llua906p6kjvhnvkbqd.apps.googleusercontent.com.json")
flow = Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid"
    ],
    redirect_uri=Config.GOOGLE_REDIRECT_URI
)

def load_comments():
    """Load comments from comments.csv."""
    comments = {}
    try:
        with open('comments.csv', mode='r') as file:
            reader = csv.DictReader(file)
            if {'product_name', 'username', 'comment'} - set(reader.fieldnames):
                raise ValueError("comments.csv is missing required headers.")

            for row in reader:
                product_name = row['product_name']
                comments.setdefault(product_name, []).append({
                    'username': row['username'],
                    'comment': row['comment']
                })
    except FileNotFoundError:
        print("comments.csv not found.")
    except ValueError as e:
        print(f"Error in loading comments: {e}")
    return comments

# Sample product data
products = {
    '1': {'id': '1', 'title': 'Product 1', 'price': '$10', 'link': 'http://example.com/product1', 'website': 'Example', 'rating': '4.5'},
    '2': {'id': '2', 'title': 'Product 2', 'price': '$20', 'link': 'http://example.com/product2', 'website': 'Example', 'rating': '4.0'},
    # Add more products as needed
}

# Routes

@app.route('/')
def landingpage():
    return render_template("./static/landing.html", login='username' in session)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        if check_user(username, request.form['password']):
            session['username'] = username
            return redirect(url_for('landingpage'))
        return render_template("./static/landing.html", login=False, invalid=True)
    return render_template('./static/login.html')


@app.route('/login/google')
def login_google():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route('/callback')
def callback():
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    request_session = requests.Request()
    id_info = id_token.verify_oauth2_token(
        credentials.id_token, request_session, flow.client_config['client_id']
    )

    
    email = id_info.get("email")
    full_name = id_info.get("name")
    given_name = id_info.get("given_name")
    family_name = id_info.get("family_name")
    profile_picture_url = id_info.get("picture")
    google_id = id_info.get("sub")  # Google unique user ID
    email_verified = id_info.get("email_verified")

    if db.user_exists(email):
        db.update_last_login(email)
        session['username'] = email
        session['user_info'] = (email ,given_name)

    else:
        # Register new user
        db.insert_user(
            email=email,
            full_name=full_name,
            name=given_name,
            email_verified=email_verified,
            profile_picture_url=profile_picture_url,
            google_id=google_id
        )
        session['username'] = email
        session['user_info'] = (email ,given_name)

    return redirect(url_for("login"))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if create_user(request.form['username'], request.form['password']):
            return redirect(url_for('login'))
        return render_template("./static/landing.html", login=False, invalid=True)
    return render_template('./static/login.html')


@app.route('/share', methods=['POST'])
def share():
    share_wishlist(session['username'], "default", request.form['email'])
    return redirect(url_for('wishlist'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landingpage'))


@app.route("/search", methods=["POST", "GET"])
def search():
    if 'username' not in session:
        return redirect(url_for('login'))

    product = request.args.get("product_name") or request.form.get("product_name")
    if not product or product == "":
        return render_template(
            "./static/result.html", error="Please enter a search term.", total_pages=0
        )
    start_time = time.time()
    data = driver(product, currency=None)
    if data is None or data.empty:
        return render_template(
            "./static/result.html", error="No results found for your search.", total_pages=0
        )
    end_time = time.time()
    processing_time = end_time - start_time
    print("Processing time:", processing_time, "seconds")

    comments = load_comments()
    total_pages = (len(data) + 19) // 20
    return render_template(
        "./static/result.html", data=data.to_dict(orient='records'), prod=product,
        total_pages=total_pages, comments=comments
    )


@app.route('/add_comment', methods=['POST'])
def add_comment():
    product_name = request.form.get('product_name')
    comment = request.form.get('comment')
    username = session.get('username')

    if product_name and comment and username:
        with open('comments.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([product_name, username, comment])

    return redirect(url_for('search'))


@app.route("/filter", methods=["POST", "GET"])
def product_search_filtered():
    product = request.args.get("product_name")
    sort = request.form.get("sort")
    currency = request.form.get("currency")
    min_price, max_price, min_rating = map(
        lambda x: float(x) if x else None, [
            request.form.get("min_price"),
            request.form.get("max_price"),
            request.form.get("min_rating")
        ]
    )
    return product_search_filtered(
        product, sort if sort != "default" else None,
        currency if currency != "usd" else None, None,
        min_price, max_price, min_rating
    )

def create_wishlist_table():
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wishlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            image TEXT,
            price TEXT,
            website TEXT,
            rating TEXT,
            added_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

# Call the function to create the table when the app starts
create_wishlist_table()


@app.route('/wishlist')
def wishlist():
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM wishlist')
    products = cursor.fetchall()

    conn.close()

    return render_template('wishlist.html', products=products)


@app.route('/add-wishlist-item', methods=['POST'])
def add_to_wishlist():
    title = request.form['title']
    img = request.form['img']
    price = request.form['price']
    website = request.form['website']
    rating = request.form['rating']
    
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO wishlist (title, image, price, website, rating)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, img, price, website, rating))

    conn.commit()
    conn.close()

    return jsonify({"message": "Product added to wishlist!"})
@app.route('/remove-wishlist-item', methods=['POST'])
def remove_wishlist_item():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized access!'}), 403
    
    product_id = request.form.get('id')
    user = db.get_user(session['username'])
    if not user:
        return jsonify({'error': 'User not found!'}), 404
    
    user_id = user[0]
    
    try:
        wishlist_items = db.get_wishlist(user_id)
        if not any(item[0] == product_id for item in wishlist_items):
            return jsonify({'error': 'Product not found in wishlist!'}), 404  # Not found status code
        
        # Remove the product from the user's wishlist in the database
        db.cursor.execute("DELETE FROM wishlist WHERE user_id = ? AND product_id = ?", (user_id, product_id))
        db.conn.commit()

        return jsonify({'message': 'Product removed from wishlist!'}), 200  # OK status code
    except Exception as e:
        db.conn.rollback()
        return jsonify({'error': f'Failed to remove product: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True)
