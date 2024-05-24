from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, RadioField

class RoleForm(FlaskForm):
    role = RadioField("Role", choices=['User', 'Moderator', 'Admin'])
    submit = SubmitField("Submit")