from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo
class UserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('password2', message='Passwords must match!')]) 
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match!')])
    submit = SubmitField("Submit")
