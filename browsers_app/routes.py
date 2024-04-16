import random
import sqlite3
from app import app, db, User, Post
from flask import make_response, request, render_template, redirect, flash, url_for
from .user_agent_handler import get_browser, get_os
from .forms import NameForm, UserForm, PasswordForm, PostForm, LoginForm, SearchForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user


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
        user = User.query.filter_by(username=form.username.data).first()
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
            return redirect(url_for('login'))
        else:
            flash("User already exists")
        
    users = User.query.order_by(User.date_added)
    return render_template('add_user.html', username=username, form=form, users=users)

@app.route("/user/update/<int:id>", methods=['GET', 'POST'])
@login_required
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
@login_required
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
@login_required
def add_post():
    form = PostForm()
    poster_id = current_user.id

    if form.validate_on_submit():
        post = Post(title = form.title.data, content=form.content.data, poster_id=poster_id, slug=form.slug.data)
        form.title.data = ''
        form.content.data = ''
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

@app.route("/post/edit/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    if current_user.id != post.poster.id:
        return redirect('/posts')
    form = PostForm()

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.slug = form.slug.data

        db.session.add(post)
        db.session.commit()

        flash ("Post has been successfully updated!")
        return redirect(url_for('post', id=post.id))
    form.title.data = post.title
    form.content.data = post.content
    form.slug.data = post.slug

    return render_template("edit_post.html", form=form)

@app.route("/post/delete/<int:id>", methods=['GET'])
@login_required
def delete_post(id):
    try:
        post_to_delete = Post.query.get_or_404(id)
        if current_user.id != post_to_delete.poster.id:
            return redirect('/posts')
        else:
            db.session.delete(post_to_delete)
            db.session.commit()

            flash("Post deleted successfully")
            return redirect("/posts")
    except:
        flash("Something went wrong")
        return redirect("/posts")

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Succesfull login")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password! Try again.")
        else:
            flash("That user does not exist! Try again")
    
    return render_template("login.html", form=form)

@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('login'))

@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    posts = Post.query
    if form.validate_on_submit():
        searched = form.searched.data
        posts = posts.filter(Post.content.like('%' + searched + '%'))
        posts = posts.order_by(Post.title).all()
        return render_template('search.html', form=form, searched=searched, posts=posts)
    pass

@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)