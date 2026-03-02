import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps

app = Flask(__name__)
app.secret_key = "secretkey123"

# Credentials
# -------------------
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

USER_NAME = "user"
USER_PASSWORD = "user123"

# Decorators
# -------------------
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session and 'admin' not in session:
            return redirect(url_for('user_login'))
        return f(*args, **kwargs)
    return decorated_function

# Default Route
# -------------------
@app.route('/')
def index():
    if 'admin' in session:
        return redirect(url_for('admin_home'))
    elif 'user' in session:
        return redirect(url_for('user_home'))
    else:
        return redirect(url_for('user_login'))
        
# User Login
# -------------------
@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == USER_NAME and password == USER_PASSWORD:
            session['user'] = username
            return redirect(url_for('home_page'))
        else:
            error = "Invalid Username or Password"

    return render_template("user_login.html", error=error)

# Admin Login
# -------------------
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = username
            return redirect(url_for('admin_home'))
        else:
            error = "Invalid Username or Password"

    return render_template("admin_login.html", error=error)

# Admin Pages
# -------------------
@app.route('/admin_home')
@admin_required
def admin_home():
    return render_template('admin_home.html')

@app.route("/maintenance")
@admin_required
def maintenance():
    return render_template("maintenance.html")

# Reports
# -------------------
@app.route("/reports")
@admin_required
def reports():
    return render_template("reports.html")

@app.route('/list_of_books')
@admin_required
def list_of_books():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM items WHERE category='Book'")
    rows = cursor.fetchall()
    conn.close()

    books = []
    for row in rows:
        books.append({
            "id": row[0],
            "name": row[1],
            "category": row[2],
            "quantity": row[3],
            "status": row[4],
            "created_at": row[5]
        })

    return render_template('list_of_books.html', books=books)
@app.route('/list_of_movies')
@admin_required
def list_of_movies():
    return render_template('list_of_movies.html')



@app.route('/active_issue')
@admin_required
def active_issue():
    return render_template('active_issue.html')

@app.route('/overdue_returns')
@admin_required
def overdue_returns():
    return render_template('overdue_returns.html')

@app.route('/pending_issue_requests')
@admin_required
def pending_issue_requests():
    return render_template('pending_issue_requests.html')

# User Home
# -------------------
@app.route('/user_home')
def home_page():
    if 'user' not in session:
        return redirect(url_for('user_login'))
    return render_template('user_home.html')

# Transactions
# -------------------
@app.route('/transactions')
@login_required
def transactions():
    return render_template('transactions.html')


# Membership
# -------------------
@app.route('/membership/add', methods=['GET', 'POST'])
@admin_required
def membership_add():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        contact_name = request.form.get('contact_name')
        contact_address = request.form.get('contact_address')
        adhar_card_no = request.form.get('adhar_card_no')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        membership_type = request.form.get('membership_type')

        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO memberships 
            (first_name, last_name, contact_name, contact_address, adhar_card_no, start_date, end_date, membership_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (first_name, last_name, contact_name, contact_address,
              adhar_card_no, start_date, end_date, membership_type))

        conn.commit()
        conn.close()

        return redirect(url_for('membership_add'))

    return render_template('add_membership.html')

@app.route('/list_of_memberships', methods=['GET', 'POST'])
@admin_required
def list_of_memberships():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM memberships')
    rows = cursor.fetchall()
    conn.close()

    memberships = []
    from datetime import datetime
    today = datetime.today()

    for row in rows:
        end_date = datetime.strptime(row[7], "%Y-%m-%d")
        status = "Active" if end_date >= today else "Inactive"

        memberships.append({
            "id": row[0],
            "name": f"{row[1]} {row[2]}",
            "contact_name": row[3],
            "contact_address": row[4],
            "adhar_card_no": row[5],
            "start_date": row[6],
            "end_date": row[7],
            "status": status,
            "amount_pending": "0"
        })

    return render_template('list_of_memberships.html', memberships=memberships)

# Membership Update 
# -------------------
@app.route('/update_membership', methods=['GET', 'POST'])
@admin_required
def membership_update_form():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        membership_id = request.form.get('membership_id')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        extension = request.form.get('extension')
        remove = request.form.get('remove')

        if remove == "yes":
            cursor.execute("DELETE FROM memberships WHERE id=?", (membership_id,))
        else:
            cursor.execute("""
                UPDATE memberships
                SET start_date=?, end_date=?, membership_type=?
                WHERE id=?
            """, (start_date, end_date, extension, membership_id))

        conn.commit()
        conn.close()

        return redirect(url_for('admin_home'))

    conn.close()
    return render_template("update_membership.html")



# Initialize database
# -------------------
def init_db():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memberships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            contact_name TEXT,
            contact_address TEXT,
            adhar_card_no TEXT,
            start_date TEXT,
            end_date TEXT,
            membership_type TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT,
            quantity INTEGER,
            status TEXT DEFAULT 'Available',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()
# Books Add
# -------------------
@app.route('/books/add', methods=['GET', 'POST'])
@admin_required
def books_add():
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        quantity = request.form.get('quantity')

        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO items (name, category, quantity)
            VALUES (?, ?, ?)
        """, (name, category, quantity))

        conn.commit()
        conn.close()

        return redirect(url_for('list_of_books'))

    return render_template('add_books.html')
# Books Update
# -------------------
@app.route('/books/update', methods=['GET', 'POST'])
@admin_required
def books_update():
    if request.method == 'POST':
        book_id = request.form.get('book_id')
        name = request.form.get('name')
        quantity = request.form.get('quantity')


        return redirect(url_for('books_update'))

    return render_template('books_update.html')



# Book Availability
# -------------------
@app.route('/book_available', methods=['GET', 'POST'])
@login_required
def book_available():
    if request.method == 'POST':
        return redirect(url_for('search_result'))
    return render_template('book_available.html')


# Search Result
# -------------------
@app.route('/search_result')
@login_required
def search_result():
    books = [
        {"name": "A", "author": "Author Name", "serial": "101", "available": "Y"},
        {"name": "A", "author": "Author Name", "serial": "102", "available": "Y"},
        {"name": "A", "author": "Author Name", "serial": "103", "available": "Y"},
        {"name": "A", "author": "Author Name", "serial": "104", "available": "N"},
    ]
    return render_template('search_result.html', books=books)

# Issue Book
# -------------------
@app.route('/issue_book')
@login_required
def issue_book():
    serial = request.args.get('serial')

    books = [
        {"name": "A", "author": "Author Name", "serial": "101", "available": "Y"},
        {"name": "A", "author": "Author Name", "serial": "102", "available": "Y"},
        {"name": "A", "author": "Author Name", "serial": "103", "available": "Y"},
        {"name": "A", "author": "Author Name", "serial": "104", "available": "N"},
    ]

    selected_book = next((book for book in books if book["serial"] == serial), None)

    return render_template("book_issue.html", book=selected_book)


# Return Book
# -------------------
@app.route('/return_book')
@login_required
def return_book():
    return render_template("return_book.html")


# Pay Fine
# -------------------
@app.route('/pay_fine')
@login_required
def pay_fine():
    return render_template("pay_fine.html")


# Submit Form
# -------------------
@app.route("/submit", methods=["POST"])
@login_required
def submit():
    book_name = request.form.get("book_name")
    return f"Form Submitted Successfully {book_name}"


# Logout
# -------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('user_login'))

    

# Run App
# -------------------
if __name__ == "__main__":
    app.run(debug=True)