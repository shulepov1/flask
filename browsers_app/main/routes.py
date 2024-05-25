import random
import sqlite3
from .. import db, mail
from . import main
from browsers_app.models import User, Post, Permission, Role
from flask import make_response, request, render_template, redirect, flash, url_for
from ..user_agent_handler import get_browser
from ..forms import NameForm, UserForm, PasswordForm, PostForm, LoginForm, SearchForm, RoleForm
from werkzeug.security import check_password_hash
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_mail import Message
from ..decorators import admin_required, permission_required

def get_db_connection():
    conn = sqlite3.connect('DB.db')
    conn.row_factory = sqlite3.Row
    return conn

@main.route("/admin")
@login_required
@admin_required
def admin():
    return "Admin only"

@main.route("/moder")
@login_required
@permission_required(Permission.MODERATE)
def moder():
    return "Moderator only"

@main.route("/")
def index():
    conn = get_db_connection()
    browsers = conn.execute('SELECT * FROM Browsers').fetchall()
    conn.close()
    user_agent_string = str(request.headers.get('User-Agent'))
    user_browser = get_browser(user_agent_string)
    response = make_response(render_template("index.html", user_browser=user_browser, browsers=browsers))
    if (user_browser == "Firefox"):
        random_float = random.random()
        response.set_cookie("flag", str(random_float)) 
    return response

@main.route("/browser/<browser>/")
def browser(browser):
    return f'<h1>page for {browser}</h1>'

@main.errorhandler(404)
def page_not_found(e):
    return render_template("/404.html"), 404

@main.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500 

@main.route("/browser/create", methods=["GET"])
def get_form():
    return render_template("browser_form.html")

@main.route("/browser/create", methods=["POST"])
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

@main.route("/send-mail-page", methods=['GET'])
def send_email_page():
    name = None
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Succesffully!")
    return render_template("form.html", name = name, form=form)

@login_required
@main.route('/send-mail', methods=['POST'])
def send_mail():
    try:
        email = request.form.get('email')
        msg = Message(request.form.get('theme'), sender='BBBlog', recipients=[email])
        msg.body = request.form.get('body') 
        mail.send(msg)
        flash("Mail sent!")
    except:
        flash("couldnt sent the email!")
    return redirect(url_for('main.send_email_page'))

@main.route("/user/update/<int:id>", methods=['GET', 'POST'])
@login_required
def update_user(id):
    form = UserForm()
    user_to_update = User.query.get_or_404(id)
    if not (current_user.can(Permission.ADMIN) or current_user.id == user_to_update.id): 
        return redirect("/dashboard")  
    if request.method == "POST":
        print(request.form)
        user_to_update.username = request.form['username']
        user_to_update.email = request.form['email']
        user_to_update.name = request.form['name']
        user_to_update.about = request.form['about']
        try:
            db.session.commit()
            flash("User updated succesfully")
            return redirect("/dashboard")
        except:
            flash("Update went wrong")
    return render_template("update_user.html", form=form, user_to_update=user_to_update, Permission=Permission)

@main.route("/user/delete/<int:id>", methods=["POST"])
@login_required
def delete_user(id):
    user_to_delete = User.query.get_or_404(id)
    if not (current_user.can(Permission.ADMIN) or current_user.id == user_to_delete.id): 
        flash("action not permitted")
        return redirect("/")
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("user has been deleted")
    except:
        flash("something went wroing")
    return redirect("/register")

@main.route("/post/add", methods=['GET', 'POST'])
@login_required
def add_post():
    if (not current_user.is_authenticated):
        flash("you're not logged in")
        return ("/dashboard")
    
    form = PostForm()
    poster_id = current_user.id

    if form.validate_on_submit():
        post = Post(title = form.title.data, content=form.content.data, poster_id=poster_id, slug=form.slug.data)
        try:
            db.session.add(post)
            db.session.commit()
            form.title.data = ''
            form.content.data = ''
            form.slug.data = ''
            flash("Post added successfully!")
        except:
            flash("something went wrong")

    return render_template("add_post.html", form=form)

@main.route("/posts", methods=['GET'])
def posts():
    posts = Post.query.order_by(Post.date_posted.desc())
    count = Post.query.count()
    return render_template("posts.html", posts=posts, count=count)

@main.route("/post/<int:id>", methods=['GET'])
def post(id):
    post = Post.query.get_or_404(id)
    return render_template("post.html", post=post)

@main.route("/post/edit/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_post(id):
    if not (current_user.can(Permission.MODERATE) or current_user.id == post.poster.id):
        return redirect('/posts')
    
    post = Post.query.get_or_404(id)
    form = PostForm()

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.slug = form.slug.data
        try:
            db.session.add(post)
            db.session.commit()
            flash ("Post has been successfully updated!")
            return redirect(url_for('main.post', id=post.id))
        except:
            flash("fields are not valid")

    form.title.data = post.title
    form.content.data = post.content
    form.slug.data = post.slug
    return render_template("edit_post.html", form=form)

@main.route("/post/delete/<int:id>", methods=['GET'])
@login_required
def delete_post(id):
    try:
        post_to_delete = Post.query.get_or_404(id)
        if not (current_user.can(Permission.MODERATE) or current_user.id == post_to_delete.poster.id):
            flash("dont have permission")
            return redirect(f"/post/{id}")
        else:
            db.session.delete(post_to_delete)
            db.session.commit()
            flash("Post deleted successfully")
            return redirect("/posts")
    except:
        flash("Something went wrong")
        return redirect("/posts")

@main.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():    
    return render_template("dashboard.html")

@main.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    posts = Post.query
    if form.validate_on_submit():
        searched = form.searched.data
        posts = posts.filter(Post.content.like('%' + searched + '%'))
        posts = posts.order_by(Post.title).all()
        return render_template('search.html', form=form, searched=searched, posts=posts)
    return redirect(request.referrer)

@main.context_processor
def base():
    # send form to base.html -> navbar.html templates
    form = SearchForm()
    return dict(form=form)

@main.route("/user/<username>", methods=['GET', 'POST'])
def user(username):
    form = RoleForm()
    user = User.query.filter_by(username=username).first_or_404()
    if not User:
        return render_template("/404.html")
    if request.method == 'POST':
        if current_user.can(Permission.ADMIN) and form.validate_on_submit():
            role = Role.query.filter_by(name=request.form['role']).first()
            user.role = role
            try:
                db.session.commit()
                flash("Update role successfully")
            except:
                flash("Couldn't update the role")
    posts = Post.query.filter_by(poster_id=user.id).all()
    
    return render_template('profile.html', user=user, posts=posts, form=form, Permission=Permission)