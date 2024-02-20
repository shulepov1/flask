from app import app
import random
from flask import make_response, request, render_template
from .user_agent_handler import get_browser, get_os

@app.route("/")
def index():
    user_agent_string = str(request.headers.get('User-Agent'))
    # user_os = get_os(user_agent_string) 
    user_browser = get_browser(user_agent_string)
    response = make_response(render_template("index.html", user_browser=user_browser))
    if (user_browser == "Firefox"):
        random_float = random.random()
        response.set_cookie("flag", str(random_float)) 
    return response

@app.route("/browser/<browser>/")
def browser(browser):
    return render_template(f"{browser}.html") 

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
