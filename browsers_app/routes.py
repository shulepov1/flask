from app import app
from app import User, Post, db
import random
import sqlite3
from flask import make_response, request, render_template, redirect, flash 
from .user_agent_handler import get_browser, get_os
from .forms.NameForm import NameForm
from .forms.UserForm import UserForm
from .forms.PasswordForm import PasswordForm
from .forms.PostForm import PostForm


from werkzeug.security import generate_password_hash, check_password_hash

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
    #s family='IBM Plex Mono'
    #s family='IBM Plex Mono'

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

@app.route("/name", methods=['GET', 'POST'])
def name():
    name = None
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Succesffully!")
    return render_template("form.html", name = name, form=form)

@app.route("/test_pw", methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    password_to_check = None
    passed = None
    user_found=None
    form = PasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        form.email.data = ''
        form.password.data = ''

        user_found = User.query.filter_by(email=email).first()

        passed = check_password_hash(user_found.password_hash, password)

    return render_template("test_pw.html", form=form, email=email, password=password, user=user_found, passed=passed)

@app.route("/user/add", methods=['GET', 'POST'])
def add_user():
    username = None
    email = None
    form = UserForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            user = User(username=form.username.data, email=form.email.data, password=form.password.data)
            db.session.add(user)
            db.session.commit()
        username = form.username.data
        form.username.data = ''
        form.email.data = ''
        form.password.data = ''
        form.password2.data = ''
        flash('User created successfully')
    users = User.query.order_by(User.date_added)
    return render_template('add_user.html', username=username, form=form, users=users)

@app.route("/user/update/<int:id>", methods=['GET', 'POST'])
def update_user(id):
    form = UserForm()
    user_to_update = User.query.get_or_404(id)
    if request.method == "POST":
        print(request.form)
        user_to_update.username = request.form['username']
        user_to_update.email = request.form['email']
        try:
            db.session.commit()
            flash("User updated succesfully")
        except:
            flash("Update went wrong")
    return render_template("update_user.html", form=form, user_to_update=user_to_update)

@app.route("/user/delete/<int:id>")
def delete_user(id):
    user_to_delete = User.query.get_or_404(id)
    username = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("user has been deleted")
    except:
        flash("something went wroing")
    users = User.query.order_by(User.date_added)
    # return render_template('add_user.html', username=username, form=form, users=users)
    return redirect("/user/add")

@app.route("/post/add", methods=['GET', 'POST'])
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        post = Post(title = form.title.data, content=form.content.data, author=form.author.data, slug=form.slug.data)
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''
        db.session.add(post)
        db.session.commit()

        flash("Post added successfully!")

    return render_template("add_post.html", form=form)

@app.route("/posts", methods=['GET'])
def posts():
    posts = Post.query.order_by(Post.date_posted)

    return render_template("posts.html", posts=posts)

@app.route("/post/<int:id>", methods=['GET'])
def post(id):
    post = Post.query.get_or_404(id)
    return render_template("post.html", post=post)