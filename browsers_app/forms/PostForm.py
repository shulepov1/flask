from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField

class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    # content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    content = CKEditorField("Body")
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")
