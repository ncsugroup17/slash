"""
Copyright (C) 2023 SE23-Team44
Licensed under the MIT License.
See the LICENSE file in the project root for the full license information.
"""
import time
import os
import csv
import sqlite3
import pandas as pd
from flask import Flask, session, render_template, request, redirect, url_for, jsonify, make_response
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests
from flask_cors import CORS
from .scraper import driver
from .features import (
    create_user, check_user, wishlist_add_item,
    read_wishlist, wishlist_remove_list, share_wishlist
)
from .config import Config
from .DatabaseManager import DatabaseManager
from dotenv import load_dotenv
import json
import requests as rq
from .scraper import searchTarget, searchWalmart
import random

load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-70b-8192" 

# Initialize Flask app
app = Flask(__name__, template_folder=".")
app.secret_key = Config.SECRET_KEY
# Configure session cookies
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Allows cookies to be sent in same-site requests
# Configure CORS to allow the frontend to access the backend API
# Include support for credentials (cookies)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:3000"}})
db = DatabaseManager()

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

@app.route('/initialize-db')
def initialize_db_route():
    print("Initialize DB route was called!")
    db.create_tables()
    return "Database tables created successfully!"

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
    # Get the redirect_uri parameter (where to return the user after auth)
    redirect_uri = request.args.get('redirect_uri', '')
    
    # Configure the OAuth flow with the right callback endpoint
    flow.redirect_uri = request.host_url.rstrip('/') + "/callback"
    
    # Include the original redirect_uri in the state parameter for later use
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent',
        state=f'redirect_uri={redirect_uri}' if redirect_uri else ''
    )
    session["state"] = state
    return redirect(authorization_url)


@app.route('/callback')
def callback():
    try:
        # Set the proper redirect URI for token exchange
        flow.redirect_uri = request.host_url.rstrip('/') + "/callback"
        
        # Extract the intended redirect destination from state
        state = request.args.get('state', '')
        redirect_uri = ''
        if state and 'redirect_uri=' in state:
            redirect_uri = state.split('redirect_uri=')[1].split('&')[0]
        
        # Process the OAuth response
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        request_session = requests.Request()
        id_info = id_token.verify_oauth2_token(
            credentials.id_token,
            request_session,
            flow.client_config['client_id'],
            clock_skew_in_seconds=60
        )
        
        # Extract user info
        email = id_info.get("email")
        full_name = id_info.get("name")
        given_name = id_info.get("given_name")
        profile_picture_url = id_info.get("picture")
        google_id = id_info.get("sub")
        email_verified = id_info.get("email_verified")

        # Update or create user
        if db.user_exists(email):
            db.update_last_login(email)
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
        
        # Set session data
        session['username'] = email
        session['user_info'] = (email, given_name)
        
        # If we have a redirect URI, go there; otherwise go to the root
        if redirect_uri:
            return redirect(redirect_uri)
        else:
            return redirect('/')
        
    except Exception as e:
        # Log any errors
        print(f"Error in callback: {str(e)}")
        # Redirect to home on error
        return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if create_user(request.form['username'], request.form['password']):
            return redirect(url_for('login'))
        return render_template("./static/landing.html", login=False, invalid=True)
    return render_template('./static/login.html')


@app.route('/share', methods=['POST'])
def share():
    try:
        # Validate session and email input
        if 'username' not in session:
            return jsonify({'error': 'User not logged in'}), 401
        
        # Get JSON data instead of form data
        data = request.json
        email = data.get('email')
        wishlist = data.get('wishlist')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400

        # Call the share_wishlist function (update if your function also needs the wishlist)
        share_wishlist(session['username'], "default", email, wishlist)
        return jsonify({'message': 'Wishlist shared successfully'}), 200
    except Exception as e:
        app.logger.error(f"Error sharing wishlist: {str(e)}", exc_info=True)
        return jsonify({'error': f'Failed to share wishlist: {str(e)}'}), 500


@app.route('/logout')
def logout():
    # Get the redirect_uri parameter 
    redirect_uri = request.args.get('redirect_uri', '/')
    
    # Clear the session
    session.clear()
    
    # Return to the specified location
    return redirect(redirect_uri)


@app.route("/search", methods=["POST", "GET"])
def search():
    # Check for JSON API request
    want_json = request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json'
    
    # For authenticated endpoints, require login
    if 'username' not in session:
        if want_json:
            return jsonify({'error': 'Authentication required'}), 401
        else:
            return redirect(url_for('login'))

    product = request.args.get("product_name") or request.form.get("product_name")
    if not product or product == "":
        if want_json:
            return jsonify({'error': 'Please enter a search term.'}), 400
        else:
            return render_template(
                "./static/result.html", error="Please enter a search term.", total_pages=0
            )
            
    start_time = time.time()
    try:
        # Use a timeout for the scraper call to prevent long-running requests
        data = driver(product, currency=None)
        
        # Check if data is None or empty DataFrame
        if data is None or (isinstance(data, pd.DataFrame) and data.empty):
            if want_json:
                return jsonify({
                    'error': 'No results found or search timed out.',
                    'products': [],
                    'product_name': product,
                    'total_pages': 0
                }), 200  # Return 200 with empty results rather than 404
            else:
                return render_template(
                    "./static/result.html", 
                    error="No results found. Please try a different search term or try again later.", 
                    total_pages=0
                )
    except Exception as e:
        # Handle any exceptions from the scraper
        print(f"Error in scraper: {str(e)}")
        if want_json:
            return jsonify({
                'error': f'Search error: {str(e)}',
                'products': [],
                'product_name': product,
                'total_pages': 0
            }), 200  # Return 200 with error message
        else:
            return render_template(
                "./static/result.html", 
                error="An error occurred while searching. Please try again later.", 
                total_pages=0
            )
            
    end_time = time.time()
    processing_time = end_time - start_time
    print("Processing time:", processing_time, "seconds")

    try:
        comments = load_comments()
    except Exception as e:
        print(f"Error loading comments: {str(e)}")
        comments = {}
    
    # Calculate total pages only if we have valid data
    total_pages = 0
    if isinstance(data, pd.DataFrame) and not data.empty:
        total_pages = (len(data) + 19) // 20
    
    # If the request wants JSON (API request), return JSON
    if want_json:
        if isinstance(data, pd.DataFrame):
            products_list = data.to_dict(orient='records')
        else:
            products_list = []
            
        return jsonify({
            'products': products_list,
            'product_name': product,
            'total_pages': total_pages,
            'comments': comments,
            'processing_time': processing_time
        })
    
    # Otherwise return the HTML template
    return render_template(
        "./static/result.html", 
        data=data.to_dict(orient='records') if isinstance(data, pd.DataFrame) and not data.empty else [], 
        prod=product,
        total_pages=total_pages, 
        comments=comments
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



@app.route('/wishlist')
def wishlist():
    # Debug session data
    app.logger.info(f"Session data in wishlist route: {session}")
    
    if 'username' not in session:
        app.logger.warning("No username in session for wishlist route")
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'error': 'You must be logged in to view your wishlist.'}), 401
        return redirect(url_for('login'))
    
    try:
        username = session.get('username')
        user_info = session.get('user_info')
        
        app.logger.info(f"Username from session: {username}")
        app.logger.info(f"User info from session: {user_info}")
        
        # Determine user email for database lookup
        user_email = None
        if user_info and isinstance(user_info, (list, tuple)) and len(user_info) > 0:
            user_email = user_info[0]
        else:
            user_email = username
            
        app.logger.info(f"Using user email for lookup: {user_email}")
        
        user = db.get_user(user_email)
        app.logger.info(f"User from database: {user}")
        
        if not user:
            app.logger.error(f"User not found in database: {user_email}")
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'error': 'User not found.'}), 404
            return redirect(url_for('login'))
            
        user_id = user[0]
        app.logger.info(f"User ID for wishlist lookup: {user_id}")
        
        wishlist_items = db.get_wishlist(user_id)
        app.logger.info(f"Wishlist items found: {len(wishlist_items)}")
        
        # If JSON is requested, return JSON
        if request.headers.get('Accept') == 'application/json':
            products_json = []
            for item in wishlist_items:
                app.logger.debug(f"Processing wishlist item: {item}")
                products_json.append({
                    'id': item[0],  # product_id
                    'title': item[1],  # name
                    'description': item[2],  # description
                    'price': item[3],  # price
                    'currency': item[4],  # currency
                    'rating': item[5],  # rating
                    'num_reviews': item[6],  # num_reviews
                    'url': item[7],  # url
                    'img': item[8],  # image_url
                    'category': item[9],  # category
                    'website': item[10]  # source
                })
            return jsonify({'products': products_json})
            
        # Otherwise, render the template
        return render_template('wishlist.html', products=wishlist_items)
        
    except Exception as e:
        app.logger.error(f"Error fetching wishlist: {str(e)}", exc_info=True)
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'error': f'Failed to load wishlist: {str(e)}'}), 500
        return render_template('wishlist.html', products=[], error=str(e))


@app.route('/add-wishlist-item', methods=['POST'])
def add_to_wishlist():
    app.logger.info(f"Session data in add-wishlist-item: {session}")

    if 'username' not in session:
        app.logger.warning("No username in session for add-wishlist-item")
        return jsonify({'error': 'Unauthorized access!'}), 401

    try:
        # Determine user email for database lookup
        username = session.get('username')
        user_info = session.get('user_info')
        
        app.logger.info(f"Username from session: {username}")
        app.logger.info(f"User info from session: {user_info}")
        
        user_email = None
        if user_info and isinstance(user_info, (list, tuple)) and len(user_info) > 0:
            user_email = user_info[0]
        else:
            user_email = username
            
        app.logger.info(f"Using user email for lookup: {user_email}")
        
        user = db.get_user(user_email)
        app.logger.info(f"User from database: {user}")
        
        if not user:
            app.logger.error(f"User not found in database: {user_email}")
            return jsonify({'error': 'User not found!'}), 404

        user_id = user[0]
        app.logger.info(f"User ID for wishlist addition: {user_id}")

        # Get product details from form
        title = request.form.get('title')
        img = request.form.get('img')
        price = request.form.get('price')
        website = request.form.get('website')
        rating = request.form.get('rating')
        url = request.form.get('url', website)  # fallback to website if url not provided
        
        app.logger.info(f"Product details: title={title}, website={website}, url={url}")

        if not all([title, img, price, website]):
            app.logger.error("Missing required product data fields")
            return jsonify({'error': 'Missing required product data!'}), 400

        # Check if product exists, create if not
        product = db.get_product(url=url)
        if not product:
            app.logger.info(f"Product not found in database, creating new product: {title}")
            db.insert_product(
                name=title, 
                description="No description available", 
                price=price,
                currency="USD", 
                rating=rating or "0", 
                num_reviews=0, 
                url=url,
                image_url=img, 
                category="Unknown", 
                source=website
            )
            product = db.get_product(url=url)
            app.logger.info(f"Created new product: {product}")

        product_id = product[0]
        app.logger.info(f"Product ID for wishlist addition: {product_id}")

        # Check if product is already in wishlist
        if db.is_product_in_wishlist(user_id, product_id):
            app.logger.warning(f"Product {product_id} already in wishlist for user {user_id}")
            return jsonify({"error": "Product is already in wishlist!"}), 409
        
        # Add product to wishlist
        db.add_to_wishlist(user_id, product_id)
        app.logger.info(f"Successfully added product {product_id} to wishlist for user {user_id}")
        return jsonify({"message": "Product added to wishlist!"}), 200
    except Exception as e:
        app.logger.error(f"Failed to add product: {str(e)}", exc_info=True)
        return jsonify({'error': f'Failed to add product: {str(e)}'}), 500

@app.route('/remove-wishlist-item', methods=['POST'])
def remove_wishlist_item():
    app.logger.info(f"Session data in remove-wishlist-item: {session}")
    
    if 'username' not in session:
        app.logger.warning("No username in session for remove-wishlist-item")
        return jsonify({'error': 'Unauthorized access!'}), 401

    product_id = request.form.get('id')
    if not product_id:
        app.logger.error("Missing product ID in remove-wishlist-item request")
        return jsonify({'error': 'Invalid product ID!'}), 400

    try:
        # Determine user email for database lookup
        username = session.get('username')
        user_info = session.get('user_info')
        
        app.logger.info(f"Username from session: {username}")
        app.logger.info(f"User info from session: {user_info}")
        app.logger.info(f"Product ID to remove: {product_id}")
        
        user_email = None
        if user_info and isinstance(user_info, (list, tuple)) and len(user_info) > 0:
            user_email = user_info[0]
        else:
            user_email = username
            
        app.logger.info(f"Using user email for lookup: {user_email}")
        
        user = db.get_user(user_email)
        app.logger.info(f"User from database: {user}")
        
        if not user:
            app.logger.error(f"User not found in database: {user_email}")
            return jsonify({'error': 'User not found!'}), 404

        user_id = user[0]
        app.logger.info(f"User ID for wishlist removal: {user_id}")

        if not db.is_product_in_wishlist(user_id, product_id):
            app.logger.warning(f"Product {product_id} not in wishlist for user {user_id}")
            return jsonify({"error": "Product not in wishlist!"}), 404

        db.remove_from_wishlist(user_id, product_id)
        app.logger.info(f"Successfully removed product {product_id} from wishlist for user {user_id}")
        return jsonify({'message': 'Product removed from wishlist!'}), 200
    except Exception as e:
        app.logger.error(f"Failed to remove product: {str(e)}", exc_info=True)
        return jsonify({'error': f'Failed to remove product: {str(e)}'}), 500

# Add a catch-all route for redirecting /login to the frontend
@app.route('/login', defaults={'path': ''})
@app.route('/login/<path:path>')
def catch_all_login(path):
    # Only redirect if this is a GET request coming directly to /login
    # POST requests should still be processed by the login function above
    if request.method == 'GET' and not request.referrer:
        print("Intercepted direct access to /login - redirecting to frontend")
        frontend_url = Config.get_frontend_url(request)
        return redirect(f"{frontend_url}/login")
    # Otherwise let the request be handled by the normal login route
    return login()

# New endpoint to handle token exchange from frontend
@app.route('/exchange-token')
def exchange_token():
    # Get the authorization code from the request
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'No code provided'}), 400
    
    try:
        # Use the config helper to determine the redirect URI
        callback_url = Config.get_frontend_url(request) + "/callback"
        
        # Create a new Flow instance with the proper redirect_uri
        exchange_flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=[
                "https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/userinfo.email",
                "openid"
            ],
            redirect_uri=callback_url
        )
        
        # Exchange the code for credentials
        exchange_flow.fetch_token(code=code)
        credentials = exchange_flow.credentials
        
        # Get user info
        request_session = requests.Request()
        id_info = id_token.verify_oauth2_token(
            credentials.id_token,
            request_session,
            exchange_flow.client_config['client_id'],
            clock_skew_in_seconds=60
        )
        
        # Process user info
        email = id_info.get("email")
        full_name = id_info.get("name")
        given_name = id_info.get("given_name")
        profile_picture_url = id_info.get("picture")
        google_id = id_info.get("sub")
        email_verified = id_info.get("email_verified")
        
        if db.user_exists(email):
            db.update_last_login(email)
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
        
        # Set session variables
        session['username'] = email
        session['user_info'] = (email, given_name)
        
        # Return success
        return jsonify({'success': True, 'username': email, 'name': given_name}), 200
    
    except Exception as e:
        print(f"Error exchanging token: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-auth')
def check_auth():
    """API endpoint to check if a user is authenticated"""
    # Check if username exists in session
    if 'username' in session:
        # Return user info
        return jsonify({
            'authenticated': True,
            'username': session['username'],
            'displayName': session.get('user_info', [None, None])[1]
        }), 200
    else:
        # Not authenticated
        return jsonify({'authenticated': False}), 401

def get_groq_headers():
    """Get headers for Groq API requests."""
    return {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
def create_system_prompt():
    return """
You are a smart, personalized shopping assistant.

Your goal is to recommend the best product for the user's needs by asking **up to 3 short, specific questions** to understand:
1. What item they are looking for
2. What occasion, purpose, or context it’s for
3. Any preference like color, style, size, or brand

Once you have collected this information, stop asking questions and generate a **single search query** that is a **concatenation of 2–3 lowercase words** without spaces. For example: "reddressparty", "bluetoothspeakeroutdoor", "coffeetablemodern".

Always respond in the following JSON format:
{
  "response": "<Your friendly message or follow-up question to the user>",
  "nextQuestion": "<The next question to ask or empty if done>",
  "searchQuery": "<3-word concatenated search query or empty if not ready>",
  "isReadyForRecommendations": <true or false>
}
"""

from urllib.parse import quote_plus

@app.route('/ai-recommendations', methods=['POST', 'OPTIONS'])
def ai_recommendations():
    if request.method == 'OPTIONS':
        return make_response('', 200)

    data = request.json
    conversation = data.get('conversation', [])

    if not conversation or not isinstance(conversation, list):
        return jsonify({'error': 'Invalid conversation data'}), 400

    # Count how many times user has responded
    num_user_turns = sum(1 for m in conversation if m.get('role') == 'user')

    # Prepare messages to send to Groq
    messages = [{"role": "system", "content": create_system_prompt()}]
    for message in conversation:
        if message['role'] in ['user', 'assistant']:
            messages.append({"role": message['role'], "content": message['content']})

    try:
        response = rq.post(
            GROQ_API_URL,
            headers=get_groq_headers(),
            json={
                "model": GROQ_MODEL,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1024,
                "response_format": {"type": "json_object"}
            },
            timeout=30
        )

        if response.status_code != 200:
            app.logger.error(f"Groq API error: {response.status_code} - {response.text}")
            return jsonify({'error': 'AI service error'}), 500

        ai_response = response.json()
        content = ai_response.get('choices', [{}])[0].get('message', {}).get('content', '{}')
        parsed_content = json.loads(content)

        if parsed_content.get('isReadyForRecommendations'):
            search_query = parsed_content.get('searchQuery', '').replace(" ", "").lower()
            print(f"🔍 Final Amazon search query: {search_query}")

            try:
                
                results = searchWalmart(search_query, df_flag=0, currency=None)

                if isinstance(results, pd.DataFrame):
                    results = results.to_dict(orient='records')  # ✅ convert to list of dicts

                recommendations = results[:6] if isinstance(results, list) else []

                structured_recommendation = [
                    {
                        "title": rec.get("title", "No title"),
                        "price": rec.get("price", "N/A"),
                        "rating": rec.get("rating") or f"{round(random.uniform(1.0, 5.0),1)}",
                        "img": rec.get("img_link", ""),
                        "link": rec.get("link", "")
                    }
                    for rec in recommendations
                ]


                print(f"Structured Recommendations {structured_recommendation}")
                # Fallback URL in case scraper missed it
                for product in recommendations:
                    if not product.get('url'):
                        product['url'] = f"https://www.amazon.com/s?k={quote_plus(search_query)}"

                return jsonify({
                    'response': f"Thanks for your answers! Based on what you told me, here are some top picks for: **{search_query}**",
                    'nextQuestion': '',
                    'recommendations': structured_recommendation
                }), 200

            except Exception as e:
                app.logger.error(f"Error fetching products from Amazon: {str(e)}")
                return jsonify({
                    'response': 'Oops! Something went wrong while searching for your products.',
                    'nextQuestion': '',
                    'recommendations': []
                }), 200


        # Otherwise, continue the conversation (ask next question)
        return jsonify({
            'response': parsed_content.get('response', ''),
            'nextQuestion': parsed_content.get('nextQuestion', ''),
            'recommendations': []
        }), 200

    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'Unexpected error occurred'}), 500

if __name__ == '__main__':
    app.run(debug=True)
