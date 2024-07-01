from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        name TEXT,
        surname TEXT,
        city TEXT,
        address TEXT,
        birth_date TEXT,
        role TEXT NOT NULL DEFAULT 'USER'
    )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def welcome():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']
    name = request.form['name']
    surname = request.form['surname']
    city = request.form['city']
    address = request.form['address']
    birth_date = request.form['birth_date']

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (email, password, name, surname, city, address, birth_date, role)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'USER')
        ''', (email, password, name, surname, city, address, birth_date))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return "User with this email already exists!"
    conn.close()
    return redirect(url_for('login_page'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        session['user_id'] = user[0]
        session['role'] = user[7]
        if session['role'] == 'ADMIN':
            return redirect(url_for('admin_homepage'))
        elif session['role'] == 'OPERATOR':
            return redirect(url_for('operator_homepage'))
        else:
            return redirect(url_for('user_homepage'))
    else:
        return "Invalid credentials!"

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('welcome'))

@app.route('/upgrade_user/<int:user_id>', methods=['POST'])
def upgrade_user(user_id):
    if 'user_id' not in session or session['role'] != 'ADMIN':
        return "Access denied!"

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role = 'OPERATOR' WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('users'))

@app.route('/users')
def users():
    if 'user_id' not in session or session['role'] != 'ADMIN':
        return "Access denied!"

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, email, name, surname, city, address, birth_date, role FROM users')
    users = cursor.fetchall()
    conn.close()

    return render_template('users.html', users=users)

@app.route('/add_admin')
def add_admin():
    email = 'admin2@example.com'
    password = 'adminpassword'
    name = 'Admin'
    surname = 'User'
    city = 'AdminCity'
    address = 'AdminAddress'
    birth_date = '2000-01-01'
    role = 'ADMIN'

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (email, password, name, surname, city, address, birth_date, role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (email, password, name, surname, city, address, birth_date, role))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return "Admin user already exists!"
    conn.close()
    return "Admin user created successfully!"

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user_id' not in session or session['role'] != 'ADMIN':
        return "Access denied!"

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('users'))



@app.route('/admin_homepage')
def admin_homepage():
    return render_template('admin_homepage.html')

@app.route('/operator_homepage')
def operator_homepage():
    return render_template('operator_homepage.html')

@app.route('/user_homepage')
def user_homepage():
    return render_template('user_homepage.html')

@app.route('/restaurants')
def restaurants():
    return render_template('restaurants.html')

@app.route('/orders')
def orders():
    return render_template('orders.html')

@app.route('/reccomandations')
def reccomandations():
    return render_template('reccomandations.html')

@app.route('/restaurant/<restaurant_name>')
def restaurant_menu(restaurant_name):
    return render_template(f'{restaurant_name}.html', restaurant_name=restaurant_name)



if __name__ == '_main_':
    app.run(debug=True)