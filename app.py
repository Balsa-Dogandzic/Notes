import markdown
from flask import Flask, render_template, request, redirect, session, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import markdown

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
    if not session.get('logged'):
        return redirect('/login/')
    cursor = mysql.connection.cursor()
    cursor.execute(f"SELECT * FROM notes WHERE user_id='{session.get('user_id')}'")
    notes = cursor.fetchall()
    cursor.close()
    return render_template("index.html", notes=notes)


@app.route('/note/<int:id>/')
def get_note(id):
    cursor = mysql.connection.cursor()
    cursor.execute(f"SELECT * FROM notes WHERE id={id}")
    note = cursor.fetchone()
    cursor.close()
    md = markdown.Markdown(extensions=["fenced_code"])
    content = md.convert(note['content'])
    response = jsonify({'title': note['title'], 'created_at':note['created_at'], 'modified_at': note['modified_at'], 'content': content})
    return response


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