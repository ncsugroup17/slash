from flask import Flask, render_template, request, redirect, url_for, session, g, send_from_directory
import os
import pymysql

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'defaultsecret')

# Database connection for MySQL (used in movie search, etc.)
def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            host=os.environ.get('MYSQL_HOST', 'database'),
            user=os.environ.get('MYSQL_USER', 'user'),
            password=os.environ.get('MYSQL_PASSWORD', 'pass'),
            database=os.environ.get('MYSQL_DATABASE', 'movies_db'),
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db

@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Public routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scientific_calculator')
def scientific_calculator():
    return render_template('scientific_calculator.html')

@app.route('/unit_converter')
def unit_converter():
    return render_template('unit_converter.html')

@app.route('/simple_games')
def simple_games():
    return render_template('simple_games.html')

@app.route('/movie_search', methods=['GET'])
def movie_search():
    query = request.args.get('q', '')
    movies = []
    error_message = None
    if query:
        # Vulnerable SQL injection demonstration (educational only)
        sql = "SELECT id, title, director, year FROM movies WHERE title LIKE '%" + query + "%'"
        db = get_db()
        try:
            with db.cursor() as cursor:
                cursor.execute(sql)
                movies = cursor.fetchall()
        except Exception as e:
            error_message = str(e)
    return render_template('movie_search.html', movies=movies, query=query, error_message=error_message)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(directory='files', path=filename, as_attachment=True)

# Admin login page (GET and POST)
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        # Check credentials from environment variables
        if username == os.environ.get('ADMIN_USERNAME') and password == os.environ.get('ADMIN_PASSWORD'):
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            error = "Invalid credentials. Please try again."
    return render_template('admin_login.html', error=error)

# Protected admin page
@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin.html')

# Admin logout
@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get('FLASK_RUN_PORT', 80))
    app.run(host='0.0.0.0', port=port)
