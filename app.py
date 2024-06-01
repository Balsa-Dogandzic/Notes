import markdown
from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL

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


@app.route('/login/')
def login():
    return render_template("login.html")


@app.route('/register')
def register():
    return render_template("register.html")


if __name__ == '__main__':
    app.run(debug=True)