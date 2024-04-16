from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired, EqualTo, Email
import email_validator
class UserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('password2', message='Passwords must match!')]) 
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match!')])
    submit = SubmitField("Submit")
