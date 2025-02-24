"""
Copyright (C) 2023 SE23-Team44
Licensed under the MIT License.
See the LICENSE file in the project root for the full license information.
"""
import time
import os
import csv
from flask import Flask, session, render_template, request, redirect, url_for
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests
from .scraper import driver
from .features import (
    create_user, check_user, wishlist_add_item,
    read_wishlist, wishlist_remove_list, share_wishlist
)
from .config import Config

# Initialize Flask app
app = Flask(__name__, template_folder=".")
app.secret_key = Config.SECRET_KEY

# Google OAuth2 setup (Use secure transport in production)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
CLIENT_SECRETS_FILE = r"/home/mesfand/Documents/slash/src/client_secret_92320207172-8cnk4c9unfaa7llua906p6kjvhnvkbqd.apps.googleusercontent.com.json"
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
    session['username'] = id_info['email']
    session['user_info'] = {'name': id_info['name'], 'email': id_info['email']}

    if not check_user(session['username'], None):
        create_user(session['username'], None, name=id_info['name'])

    return redirect(url_for("login"))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if create_user(request.form['username'], request.form['password']):
            return redirect(url_for('login'))
        return render_template("./static/landing.html", login=False, invalid=True)
    return render_template('./static/login.html')


@app.route('/wishlist')
def wishlist():
    username = session.get('username')
    wishlist_name = session.get('wishlist_name', 'default')
    items = read_wishlist(username, wishlist_name)
    items = items.to_dict('records') if not items.empty else []
    return render_template('wishlist.html', items=items)


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
    if not product:
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


@app.route("/add-wishlist-item", methods=["POST"])
def add_wishlist_item():
    wishlist_add_item(session['username'], 'default', request.form.to_dict())
    return ""


@app.route("/delete-wishlist-item", methods=["POST"])
def remove_wishlist_item():
    wishlist_remove_list(session['username'], 'default', int(request.form["index"]))
    return redirect(url_for('wishlist'))


if __name__ == '__main__':
    app.run(debug=True)
