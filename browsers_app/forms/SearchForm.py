from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo

class SearchForm(FlaskForm):
    searched=StringField("Searched", validators=[DataRequired()])
    submit=SubmitField()