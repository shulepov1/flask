from app import app
import random
import sqlite3
from flask import make_response, request, render_template, redirect
from .user_agent_handler import get_browser, get_os

def get_db_connection():
    conn = sqlite3.connect('DB.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    conn = get_db_connection()
    browsers = conn.execute('SELECT * FROM Browsers').fetchall()
    conn.close()
    user_agent_string = str(request.headers.get('User-Agent'))
    # user_os = get_os(user_agent_string) 
    user_browser = get_browser(user_agent_string)
    response = make_response(render_template("index.html", user_browser=user_browser, browsers=browsers))
    if (user_browser == "Firefox"):
        random_float = random.random()
        response.set_cookie("flag", str(random_float)) 
    return response

@app.route("/browser/<browser>/")
def browser(browser):
    return f'<h1>page for {browser}</h1>'

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500

@app.route("/browser/create", methods=["GET"])
def get_form():
    return render_template("browser_form.html")

@app.route("/browser/create", methods=["POST"])
def post_form():
    name_value = request.form['name']
    url_value = request.form['url']
    if name_value and url_value and url_value.endswith('.png'):
        conn = get_db_connection()
        conn.execute('INSERT INTO Browsers (name, url) VALUES (?, ?)', (name_value, url_value))
        conn.commit()
        conn.close()
        return redirect("/")
    else:
        return redirect("/browser/create")

    
