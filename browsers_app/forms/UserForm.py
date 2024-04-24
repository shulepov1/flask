from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired, EqualTo, Email, Length, ValidationError
import email_validator
from browsers_app.models import User
class UserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=5, max=25)])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=16), EqualTo('password2', message='Passwords must match!')]) 
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match!')])
    submit = SubmitField("Submit")
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')