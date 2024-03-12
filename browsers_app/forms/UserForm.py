from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class UserForm(FlaskForm):
    username = StringField("What's your username?", validators=[DataRequired()])
    email = StringField("What's your email?", validators=[DataRequired()])
    submit = SubmitField("Submit")
