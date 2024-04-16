from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_ckeditor import CKEditor

app = Flask(__name__)
ckeditor = CKEditor(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ilyapostgres@localhost/flaskmpgu'
app.config['SECRET_KEY'] = 'temp_key'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='poster')

    @property
    def password(self):
        raise AttributeError("property is not readable")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password, "pbkdf2")

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return 'Name: password.getter%r' % self.username

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    content = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(256))
    poster_id = db.Column(db.Integer, db.ForeignKey('user.id'))

from browsers_app import routes

