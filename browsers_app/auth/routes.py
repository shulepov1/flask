from browsers_app.models import User
from . import auth
from ..forms import UserForm, LoginForm
from .. import db
from flask import flash, redirect, render_template, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, login_required, logout_user

@auth.route("/user/add", methods=['GET', 'POST'])
def add_user():
    form = UserForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            user = User(username=form.username.data, email=form.email.data, password=form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('User created successfully')
            return redirect(url_for('auth.login'))
    else:
        if form.username.data:
            flash("Something went wrong")

    users = User.query.order_by(User.date_added)
    return render_template('add_user.html', form=form, users=users)


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