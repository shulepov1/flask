from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timezone

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

    def __repr__(self):
        return 'Name: %r' % self.username

from browsers_app import routes

