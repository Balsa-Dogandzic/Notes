import markdown
from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_url_path='/static/')
app.config['SECRET_KEY'] = '88932b3fa37fc7378ede32684eaa9972'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'notes'
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

@app.route('/')
def notes_page():
    return render_template("index.html")


# Autentifikacija


@app.route('/login/', methods=['GET', 'POST'])
def login():
    message = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute(f"SELECT * FROM users WHERE username='{username}'")
        user = cursor.fetchone()
        cursor.close()
        if user and check_password_hash(user.get('password'), password):
            session['logged'] = True
            session['user_id'] = user.get('id')
            return redirect("/")
        message = "Wrong username or password."
    if session.get('logged'):
        return redirect("/")
    return render_template("login.html", message=message)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    message = ""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')
        if username == '' or email == '' or password == '':
            message = 'All fields are required.'
        elif password != confirm_password:
            message = 'Passwords do not match.'
        else:
            try:
                hashed_password = generate_password_hash(password)
                cursor = mysql.connection.cursor()
                cursor.execute(f"INSERT INTO users VALUES (NULL,'{username}','{email}','{hashed_password}')")
                mysql.connection.commit()
                cursor.close()
                return redirect("/login/")
            except:
                message = 'Username and email must be unique'
    if session.get('logged'):
        return redirect("/")
    return render_template("register.html", message=message)


@app.route('/logout/')
def logout():
    session.pop('logged', None)
    session.pop('user_id', None)
    return redirect('/login/')


if __name__ == '__main__':
    app.run(debug=True)