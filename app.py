import markdown
from flask import Flask, render_template, request, redirect, session, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import markdown, datetime, re

app = Flask(__name__, static_url_path='/static/')
app.config['SECRET_KEY'] = '88932b3fa37fc7378ede32684eaa9972'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'notes'
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)


def escape_special_characters(text):
    escape_dict = {
        '\\': '\\\\',
        '\'': '\\\'',
        '\"': '\\\"',
        '\n': '\\n',
        '\r': '\\r',
        '\x00': '\\0',
        '\x1a': '\\Z'
    }
    regex = re.compile('|'.join(re.escape(key) for key in escape_dict.keys()))
    return regex.sub(lambda match: escape_dict[match.group(0)], text)


@app.route('/about/')
def about():
    return render_template("about.html")


@app.route('/')
def notes_page():
    if not session.get('logged'):
        return redirect('/login/')
    cursor = mysql.connection.cursor()
    cursor.execute(f"SELECT * FROM notes WHERE user_id={session.get('user_id')} ORDER BY modified_at DESC")
    notes = cursor.fetchall()
    cursor.close()
    return render_template("index.html", notes=notes)


@app.route('/note/<int:id>/')
def get_note(id):
    cursor = mysql.connection.cursor()
    cursor.execute(f"SELECT * FROM notes WHERE id={id}")
    note = cursor.fetchone()
    cursor.execute(f"SELECT tags.tag FROM note_tags JOIN tags ON tags.id = note_tags.tag_id WHERE note_id={id}")
    tags = cursor.fetchall()
    cursor.close()
    md = markdown.Markdown(extensions=["fenced_code"])
    content = md.convert(note['content'])
    response = jsonify({'title': note['title'], 'created_at':note['created_at'], 'modified_at': note['modified_at'], 'tags': tags, 'content': content})
    return response


@app.route('/note/add/', methods=['GET', 'POST'])
def add_note():
    if request.method == 'POST':
        title = escape_special_characters(request.form['title'])
        checked_tags = request.form.getlist('tags')
        note = escape_special_characters(request.form['note'])
        today = datetime.datetime.now()
        cursor = mysql.connection.cursor()
        cursor.execute(f"INSERT INTO notes VALUES (NULL,'{title}','{note}', '{today}', '{today}', {session.get('user_id')})")
        mysql.connection.commit()
        memo_id = cursor.lastrowid
        for tag in checked_tags:
            cursor.execute(f"INSERT INTO note_tags VALUES (NULL, {memo_id}, {tag})")
            mysql.connection.commit()
        cursor.close()
        return redirect("/")
    cursor = mysql.connection.cursor()
    cursor.execute(f"SELECT * FROM tags ORDER BY tag")
    tags = cursor.fetchall()
    cursor.close()
    if not session.get('logged'):
        return redirect('/login/')
    return render_template("add_note.html", tags=tags)


@app.route('/note/update/<int:id>/', methods=['GET', 'POST'])
def update_note(id):
    if request.method == 'POST':
        title = escape_special_characters(request.form['title'])
        note = escape_special_characters(request.form['note'])
        today = datetime.datetime.now()
        cursor = mysql.connection.cursor()
        cursor.execute(f"UPDATE notes SET title='{title}', content='{note}', modified_at='{today}' WHERE id={id}")
        mysql.connection.commit()
        return redirect("/")
    cursor = mysql.connection.cursor()
    cursor.execute(f"SELECT * FROM notes WHERE id={id}")
    note = cursor.fetchone()
    cursor.close()
    if not session.get('logged'):
        return redirect('/login/')
    return render_template("update_note.html", note=note)


@app.route('/note/delete/<int:id>/')
def delete_note(id):
    if not session.get('logged'):
        return redirect('/login/')
    cursor = mysql.connection.cursor()
    cursor.execute(f"DELETE FROM notes WHERE id={id}")
    mysql.connection.commit()
    return redirect('/')


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