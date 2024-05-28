import random
import urllib
import sqlite3
from .. import db, mail
from . import main
from browsers_app.models import User, Post, Permission, Role
from flask import make_response, request, render_template, redirect, flash, url_for
from ..user_agent_handler import get_browser
from ..forms import NameForm, UserForm, PostForm, SearchForm, RoleForm
from flask_login import login_required, current_user
from flask_mail import Message
from ..decorators import admin_required, permission_required

from flask import Flask, request, Response
import requests

# app = Flask(__name__)
# API_HOST = "http://95.164.89.123:8888"  # Replace with the actual API host

# @main.route('/', defaults={'path': ''}, methods=["GET", "POST"])
# @main.route('/<path:path>', methods=["GET", "POST"])
# def proxy_to_API_HOST(path):
#     res = requests.request(
#         method=request.method,
#         url=request.url.replace(request.host_url, f'{API_HOST}/'),
#         headers={k: v for k, v in request.headers if k.lower() != 'host'},
#         data=request.get_data(),
#         cookies=request.cookies,
#         allow_redirects=False,
#     )
#     print(res.url)
#     print("here")
#     excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
#     response_headers = [(name, value) for name, value in res.raw.headers.items() if name.lower() not in excluded_headers]

#     return Response(res.content, status=res.status_code, headers=response_headers)

def get_db_connection():
    """
    подключение к sqlite
    конфиг. чтоб строки возвращались как объекты класса Row
    """
    conn = sqlite3.connect('DB.db')
    conn.row_factory = sqlite3.Row
    return conn


# @main.route("/admin")
# @login_required
# @admin_required
# def admin():
#     """
#     тестовый View только для роли ADMIN
#     """
#     return "Admin only"


# @main.route("/moder")
# @login_required
# @permission_required(Permission.MODERATE)
# def moder():
#     """
#     тестовый View только для роли MODERATOR
#     """
    # return "Moderator only"


@main.route("/")
def index():
    """
    Главная страница, фетчит данные о браузерах с sqlite
    считывает User-Agent из request headers, чтобы узнать браузер пользователя
    если firefox set cookie "flag" рандомный float
    """

    conn = get_db_connection()
    browsers = conn.execute('SELECT * FROM Browsers').fetchall()
    conn.close()
    user_agent_string = str(request.headers.get('User-Agent'))
    user_browser = get_browser(user_agent_string)
    response = make_response(render_template(
        "index.html", user_browser=user_browser, browsers=browsers))
    if (user_browser == "Firefox"):
        random_float = random.random()
        response.set_cookie("flag", str(random_float))
    return response


@main.route("/browser/<browser>/")
def browser(browser):
    """
    страница для браузера
    """
    return f'<h1>page for {browser}</h1>'


@main.route("/browser/create", methods=["GET"])
def get_form():
    """
    страница с формой для добавления нового браузера
    """
    return render_template("browser_form.html")


@main.route("/browser/create", methods=["POST"])
def post_form():
    """
    обработка POST запроса для страницы с формой
    для нового браузера
    добавляет данные из формы в бд
    """
    name_value = request.form['name']
    url_value = request.form['url']
    if name_value and url_value and url_value.endswith('.png'):
        conn = get_db_connection()
        conn.execute('INSERT INTO Browsers (name, url) VALUES (?, ?)',
                     (name_value, url_value))
        conn.commit()
        conn.close()
        return redirect("/")
    
    return redirect("/browser/create")


@main.route("/send-mail-page", methods=['GET', 'POST'])
def send_email_page():
    """
    страница для отображения формы для
    отправки письма по эл. почте
    поля формы определены в template, а не фласк форме
    """
    if request.method == "POST":
        try:
            email = request.form.get('email')
            msg = Message(request.form.get('theme'),
                        sender='BBBlog', recipients=[email])
            msg.body = request.form.get('body')
            mail.send(msg)
            flash("Mail sent!")
        except:
            flash("couldnt sent the email!")

    return render_template("form.html")


@main.route("/user/update/<int:id>", methods=['GET', 'POST'])
@login_required
def update_user(id):
    """
    форма для обновления данных о пользователе
    доступна толко админам и самому пользователю
    """
    form = UserForm()
    user_to_update = User.query.get_or_404(id)

    if not (current_user.can(Permission.ADMIN) or current_user.id == user_to_update.id):
        return redirect("/dashboard")
    if request.method == "POST":
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
    return render_template("update_user.html", form=form, user_to_update=user_to_update)


@main.route("/user/delete/<int:id>", methods=["POST"])
@login_required
def delete_user(id):
    """
    POST route для удаления пользователя
    доступ у админов и самого пользователя
    """
    user_to_delete = User.query.get_or_404(id)
    if not (current_user.can(Permission.ADMIN) or current_user.id == user_to_delete.id):
        flash("action not permitted")
        return redirect(request.referrer)
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
    """
    Страница для добавления нового поста
    """
    if not current_user.is_authenticated:
        flash("you're not logged in")
        return ("/dashboard")

    form = PostForm()
    poster_id = current_user.id

    if form.validate_on_submit():
        post_ = Post(title=form.title.data, content=form.content.data,
                    poster_id=poster_id, slug=form.slug.data)
        try:
            db.session.add(post_)
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
    """
    отображение списка всех постов
    """
    posts_ = Post.query.order_by(Post.date_posted.desc())
    count = Post.query.count()
    return render_template("posts.html", posts=posts_, count=count)


@main.route("/post/<int:id>", methods=['GET'])
def post(id):
    """
    отображение конкретного поста
    """
    post = Post.query.get_or_404(id)
    return render_template("post.html", post=post)


@main.route("/post/edit/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_post(id):
    """
    страница для редактирования поста
    доступна автору поста и модераторам, админам
    """
    

    post_ = Post.query.get_or_404(id)
    form = PostForm()
    if not (current_user.can(Permission.MODERATE) or current_user.id == post_.poster.id):
        return redirect('/posts')

    if form.validate_on_submit():
        post_.title = form.title.data
        post_.content = form.content.data
        post_.slug = form.slug.data
        try:
            db.session.add(post_)
            db.session.commit()
            flash("Post has been successfully updated!")
            return redirect(url_for('main.post', id=post_.id))
        except:
            flash("fields are not valid")

    form.title.data = post_.title
    form.content.data = post_.content
    form.slug.data = post_.slug
    return render_template("edit_post.html", form=form)


@main.route("/post/delete/<int:id>", methods=['GET'])
@login_required
def delete_post(id):
    """
    Страница для удаления поста
    доступна автору поста и модераторам, админам
    """
    try:
        post_to_delete = Post.query.get_or_404(id)
        
        if not (current_user.can(Permission.MODERATE) or current_user.id == post_to_delete.poster.id):
            flash("dont have permission")
            return redirect(f"/post/{id}")
        
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
    """
    Dashboard пользователя (пока только данные аккаунта)
    """
    return render_template("dashboard.html")


@main.route('/search', methods=['POST'])
def search():
    """
    action для формы поиска из navbar
    """
    form = SearchForm()
    posts_ = Post.query
    if form.validate_on_submit():
        searched = form.searched.data
        posts_ = posts_.filter(Post.content.like('%' + searched + '%'))
        posts_ = posts_.order_by(Post.title).all()
        return render_template('search.html', form=form, searched=searched, posts=posts_)
    return redirect(request.referrer)


@main.route("/user/<username>", methods=['GET', 'POST'])
def user(username):
    """
    Страница для отображения данных пользователя
    """
    form = RoleForm()
    user_ = User.query.filter_by(username=username).first_or_404()

    if request.method == 'POST':
        if current_user.can(Permission.ADMIN) and form.validate_on_submit():
            role = Role.query.filter_by(name=request.form['role']).first()
            user_.role = role
            try:
                db.session.commit()
                flash("Update role successfully")
            except:
                flash("Couldn't update the role")
    posts_ = Post.query.filter_by(poster_id=user_.id).all()

    return render_template('profile.html', user=user_, posts=posts_, form=form)
