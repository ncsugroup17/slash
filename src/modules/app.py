# """
# Copyright (C) 2023 SE23-Team44
 
# Licensed under the MIT License.
# See the LICENSE file in the project root for the full license information.
# """
# import os
# print("Current Working Directory:", os.getcwd())
# print("File Exists:", os.path.exists("C:\\Users\\Desmond\\Desktop\\Yaswanth\\slash\\src\\client_secret_92320207172-8cnk4c9unfaa7llua906p6kjvhnvkbqd.apps.googleusercontent.com.json"))

# from flask import Flask, session, render_template, request, redirect, url_for
# from google.oauth2 import id_token
# from google_auth_oauthlib.flow import Flow
# from google.auth.transport import requests
# import os
# from .scraper import driver, filter
# from .formatter import formatResult
# import json
# from .features import create_user, check_user, wishlist_add_item, read_wishlist, wishlist_remove_list, share_wishlist
# from .config import Config

# CLIENT_SECRETS_FILE = r"C:\Users\Desmond\Desktop\Yaswanth\slash\src\client_secret_92320207172-8cnk4c9unfaa7llua906p6kjvhnvkbqd.apps.googleusercontent.com.json"

# app = Flask(__name__, template_folder=".")
# app.secret_key = Config.SECRET_KEY

# # Google OAuth2 setup
# os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # Only for testing; remove for production
# CLIENT_SECRETS_FILE = "client_secret.json"  # Make sure this file is in your project root

# flow = Flow.from_client_secrets_file(
#     r"C:\Users\Desmond\Desktop\Yaswanth\slash\src\client_secret_92320207172-8cnk4c9unfaa7llua906p6kjvhnvkbqd.apps.googleusercontent.com.json",
#     scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
#     redirect_uri=Config.GOOGLE_REDIRECT_URI
# )

# # Landing Page
# @app.route('/')
# def landingpage():
#     login = 'username' in session
#     return render_template("./static/landing.html", login=login)


# # Traditional login route
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         session['username'] = request.form['username']
#         if check_user(request.form['username'], request.form['password']):
#             return redirect(url_for('landingpage'))
#         else:
#             return render_template("./static/landing.html", login=False, invalid=True)
#     return render_template('./static/login.html')


# # Google login route
# @app.route('/login/google')
# def login_google():
#     authorization_url, state = flow.authorization_url()
#     session["state"] = state
#     return redirect(authorization_url)

# # @app.route('/callback')
# # def callback():
# #     flow.fetch_token(authorization_response=request.url)
# #     credentials = flow.credentials
# #     request_session = requests.Request()

# #     # Verify and get user info
# #     id_info = id_token.verify_oauth2_token(
# #         credentials.id_token, request_session, flow.client_id
# #     )
    
# #     # Extracting user details
# #     user_email = id_info.get('email')
# #     user_name = id_info.get('name')
    
# #     # Store the information in the session and, optionally, in your database
# #     session['username'] = user_email
# #     session['user_info'] = {'name': user_name, 'email': user_email}
    
# #     # Optional: Call create_user function if new users need to be registered
# #     # Assuming create_user can handle Google OAuth users by just email and name.
# #     if not check_user(user_email, None):
# #         create_user(user_email, None, name=user_name)  # Modify create_user to handle Google users
    
# #     return redirect(url_for("landingpage"))

# # Google OAuth callback route
# @app.route('/callback')
# def callback():
#     flow.fetch_token(authorization_response=request.url)
#     credentials = flow.credentials
#     request_session = requests.Request()

#     # Get user information from Google
#     id_info = id_token.verify_oauth2_token(
#         credentials.id_token, request_session, flow.client_config['client_id']
#     )
    
#     session['username'] = id_info['email']
#     session['user_info'] = {'name': id_info['name'], 'email': id_info['email']}

#     # Check if user has a directory with cred.csv; create if not
#     if not check_user(session['username'], None):
#         create_user(session['username'], None, name=id_info['name'])

#     return redirect(url_for("search"))

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         session['username'] = request.form['username']
#         if create_user(request.form['username'], request.form['password']):
#             return redirect(url_for('login'))
#         else:
#             return render_template("./static/landing.html", login=False, invalid=True)
#     return render_template('./static/login.html')


# @app.route('/wishlist')
# def wishlist():
#     username = session['username']
#     wishlist_name = "default"
#     items = read_wishlist(username, wishlist_name).to_dict('records')
#     return render_template('./static/wishlist.html', data=items)


# @app.route('/share', methods=['POST'])
# def share():
#     username = session['username']
#     wishlist_name = "default"
#     email_receiver = request.form['email']
#     share_wishlist(username, wishlist_name, email_receiver)
#     return redirect(url_for('wishlist'))


# # Logout route
# @app.route('/logout')
# def logout():
#     session.clear()
#     return redirect(url_for('landingpage'))


# # @app.route("/search", methods=["POST", "GET"])
# # def product_search(new_product="", sort=None, currency=None, num=None, min_price=None, max_price=None, min_rating=None):
# #     product = request.args.get("product_name") or new_product
# #     data = driver(product, currency, num, 0, False, None, True, sort)

# #     if min_price is not None or max_price is not None or min_rating is not None:
# #         data = filter(data, min_price, max_price, min_rating)

# #     return render_template("./static/result.html", data=data, prod=product, total_pages=len(data) // 20)

# # Search route example

# @app.route("/search", methods=["POST", "GET"])
# def search():
#     if 'username' not in session:
#         return redirect(url_for('login'))

#     # Get search term from request
#     product = request.args.get("product_name") if request.method == "GET" else None
#     if product is None and request.method == "POST":
#         product = request.form.get("product_name")

#     # Handle missing or empty product
#     if not product:
#         # Define `total_pages` here even if no search term is provided
#         return render_template("./static/result.html", error="Please enter a search term.", total_pages=0)

#     # Run the search if product is valid
#     data = driver(product, currency=None)  # Adjust based on `driver` requirements

#     # Calculate total pages for pagination
#     results_per_page = 20
#     total_pages = (len(data) + results_per_page - 1) // results_per_page  # Round up

#     return render_template("./static/result.html", data=data, prod=product, total_pages=total_pages)

# from flask import send_from_directory

# @app.route("/filter", methods=["POST", "GET"])
# def product_search_filtered():
#     product = request.args.get("product_name")
#     sort = request.form.get("sort", None)
#     currency = request.form.get("currency", None)
#     min_price = request.form.get("min_price")
#     max_price = request.form.get("max_price")
#     min_rating = request.form.get("min_rating")

#     try:
#         min_price = float(min_price)
#     except (TypeError, ValueError):
#         min_price = None

#     try:
#         max_price = float(max_price)
#     except (TypeError, ValueError):
#         max_price = None

#     try:
#         min_rating = float(min_rating)
#     except (TypeError, ValueError):
#         min_rating = None

#     return product_search(product, sort if sort != "default" else None, currency if currency != "usd" else None, None, min_price, max_price, min_rating)


# @app.route("/add-wishlist-item", methods=["POST"])
# def add_wishlist_item():
#     username = session['username']
#     item_data = request.form.to_dict()
#     wishlist_name = 'default'
#     wishlist_add_item(username, wishlist_name, item_data)
#     return ""


# @app.route("/delete-wishlist-item", methods=["POST"])
# def remove_wishlist_item():
#     username = session['username']
#     index = int(request.form["index"]) 
#     wishlist_name = 'default'
#     wishlist_remove_list(username, wishlist_name, index)
#     return redirect(url_for('wishlist'))


# if __name__ == '__main__':
#     app.run(debug=True)

"""
Copyright (C) 2023 SE23-Team44

Licensed under the MIT License.
See the LICENSE file in the project root for the full license information.
"""
import os
from flask import Flask, session, render_template, request, redirect, url_for
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests
from .scraper import driver, filter
from .formatter import formatResult
from .features import create_user, check_user, wishlist_add_item, read_wishlist, wishlist_remove_list, share_wishlist
from .config import Config

# Initialize Flask app
app = Flask(__name__, template_folder=".")
app.secret_key = Config.SECRET_KEY

# Google OAuth2 setup
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # Only for testing; remove for production
flow = Flow.from_client_secrets_file(
    r"C:\Users\Desmond\Desktop\Yaswanth\slash\src\client_secret_92320207172-8cnk4c9unfaa7llua906p6kjvhnvkbqd.apps.googleusercontent.com.json",
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri=Config.GOOGLE_REDIRECT_URI
)

# Landing Page
@app.route('/')
def landingpage():
    login = 'username' in session
    return render_template("./static/landing.html", login=login)


# Traditional login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        if check_user(request.form['username'], request.form['password']):
            return redirect(url_for('landingpage'))
        else:
            return render_template("./static/landing.html", login=False, invalid=True)
    return render_template('./static/login.html')


# Google login route
@app.route('/login/google')
def login_google():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


# Google OAuth callback route
@app.route('/callback')
def callback():
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    request_session = requests.Request()

    # Get user information from Google
    id_info = id_token.verify_oauth2_token(
        credentials.id_token, request_session, flow.client_config['client_id']
    )
    
    session['username'] = id_info['email']
    session['user_info'] = {'name': id_info['name'], 'email': id_info['email']}

    # Check if user has a directory with cred.csv; create if not
    if not check_user(session['username'], None):
        create_user(session['username'], None, name=id_info['name'])

    return redirect(url_for("search"))


# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        session['username'] = request.form['username']
        if create_user(request.form['username'], request.form['password']):
            return redirect(url_for('login'))
        else:
            return render_template("./static/landing.html", login=False, invalid=True)
    return render_template('./static/login.html')


# Wishlist route
@app.route('/wishlist')
def wishlist():
    username = session['username']
    wishlist_name = "default"
    items = read_wishlist(username, wishlist_name).to_dict('records')
    return render_template('./static/wishlist.html', data=items)


# Share wishlist route
@app.route('/share', methods=['POST'])
def share():
    username = session['username']
    wishlist_name = "default"
    email_receiver = request.form['email']
    share_wishlist(username, wishlist_name, email_receiver)
    return redirect(url_for('wishlist'))


# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landingpage'))


# Search route
# @app.route("/search", methods=["POST", "GET"])
# def search():
#     if 'username' not in session:
#         return redirect(url_for('login'))

#     # Get search term from request
#     product = request.args.get("product_name") if request.method == "GET" else None
#     if product is None and request.method == "POST":
#         product = request.form.get("product_name")

#     # Handle missing or empty product
#     if not product:
#         # Define `total_pages` here even if no search term is provided
#         return render_template("./static/result.html", error="Please enter a search term.", total_pages=0)

#     # Run the search if product is valid
#     data = driver(product, currency=None)  # Adjust based on `driver` requirements

#     # Calculate total pages for pagination
#     results_per_page = 20
#     total_pages = (len(data) + results_per_page - 1) // results_per_page  # Round up

#     return render_template("./static/result.html", data=data, prod=product, total_pages=total_pages)

# Search route
# Search route
@app.route("/search", methods=["POST", "GET"])
def search():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Get search term from request
    product = request.args.get("product_name") if request.method == "GET" else None
    if product is None and request.method == "POST":
        product = request.form.get("product_name")

    # Handle missing or empty product
    if not product:
        return render_template("./static/result.html", error="Please enter a search term.", total_pages=0)

    # Run the search if product is valid
    data = driver(product, currency=None)

    # Check if `data` is empty
    if data is None or data.empty:
        return render_template("./static/result.html", error="No results found for your search.", total_pages=0)

    # Calculate total pages for pagination
    results_per_page = 20
    total_pages = (len(data) + results_per_page - 1) // results_per_page  # Round up

    return render_template("./static/result.html", data=data.to_dict(orient='records'), prod=product, total_pages=total_pages)


# Filtered search route
@app.route("/filter", methods=["POST", "GET"])
def product_search_filtered():
    product = request.args.get("product_name")
    sort = request.form.get("sort", None)
    currency = request.form.get("currency", None)
    min_price = request.form.get("min_price")
    max_price = request.form.get("max_price")
    min_rating = request.form.get("min_rating")

    try:
        min_price = float(min_price)
    except (TypeError, ValueError):
        min_price = None

    try:
        max_price = float(max_price)
    except (TypeError, ValueError):
        max_price = None

    try:
        min_rating = float(min_rating)
    except (TypeError, ValueError):
        min_rating = None

    return product_search_filtered(product, sort if sort != "default" else None, currency if currency != "usd" else None, None, min_price, max_price, min_rating)


# Add item to wishlist
@app.route("/add-wishlist-item", methods=["POST"])
def add_wishlist_item():
    username = session['username']
    item_data = request.form.to_dict()
    wishlist_name = 'default'
    wishlist_add_item(username, wishlist_name, item_data)
    return ""


# Remove item from wishlist
@app.route("/delete-wishlist-item", methods=["POST"])
def remove_wishlist_item():
    username = session['username']
    index = int(request.form["index"]) 
    wishlist_name = 'default'
    wishlist_remove_list(username, wishlist_name, index)
    return redirect(url_for('wishlist'))


if __name__ == '__main__':
    app.run(debug=True)

