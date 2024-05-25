from flask_wtf import FlaskForm
from wtforms import SubmitField, RadioField


class RoleForm(FlaskForm):
    role = RadioField("Role", choices=['User', 'Moderator', 'Admin'])
    submit = SubmitField("Submit")
