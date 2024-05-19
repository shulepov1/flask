from browsers_app.models import User
from . import auth
from ..forms import UserForm, LoginForm
from .. import db, mail 
from flask import flash, redirect, render_template, url_for, request
from flask_mail import Message
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, login_required, logout_user, current_user

def send_mail(to, subject, template, **kwargs):
    msg = Message(subject, sender='fwson12@gmail.com', recipients=[to])
    # msg.html = render_template("confirm.html", **kwargs)
    msg.body = render_template("confirm.txt", **kwargs)
    mail.send(msg)
def send_confirm(user, token):
    send_mail(user.email, "Confirm your account", 'confirm', user=user, token=token)
    redirect(url_for('main.dashboard'))

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if current_user.confirmed and request.blueprint != 'auth' and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))

@auth.route("/register", methods=['GET', 'POST'])
def add_user():
    form = UserForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            user = User(username=form.username.data, email=form.email.data, password=form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('User created successfully')
            flash('Вам на почту выслано письмо с подтверждением.')
            token = user.generate_confirmation_token()
            send_confirm(user, token)
            return redirect(url_for('auth.login'))
    else:
        if form.username.data:
            flash("Something went wrong")

    users = User.query.order_by(User.date_added)
    return render_template('add_user.html', form=form, users=users)

@auth.route("/confirm/<token>")
@login_required
def confirm(token):
    print(token)
    print(current_user.is_authenticated)
    if current_user.confirmed:
        return redirect(url_for('main.dashboard'))
    if current_user.confirm(token):
        db.session.commit()
        flash("Ваша учетная запись подтверждена")
    else:
        flash("Ваша ссылка не валидна или истекла")
    return redirect(url_for('main.dashboard'))

@auth.route("/unconfirmed")
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Succesfull login")
                return redirect(url_for('main.dashboard'))
            else:
                flash("Wrong Password! Try again.")
        else:
            flash("That user does not exist! Try again")
    
    return render_template("login.html", form=form)

@auth.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('auth.login'))


@auth.route("/secret")
@login_required
def secret():
    print("test login")
    return "Only for auth"

@auth.route("/testConfirm")
@login_required
def testConfirm():
    user = User.query.filter_by().first()
    tmp = user.generate_confirmation_token()
    user.confirm(tmp)
    return "Only for auth"
