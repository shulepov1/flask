from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ilyapostgres@localhost/flaskmpgu'
app.config['SECRET_KEY'] = 'temp_key'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    migration_test = db.Column(db.String(50), nullable=True, default='', unique=False)
    date_added = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    password_hash = db.Column(db.String(128))

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

from browsers_app import routes

