from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_ckeditor import CKEditor
from flask_mail import Mail
from authlib.integrations.flask_client import OAuth

db = SQLAlchemy()
login_manager = LoginManager()
ckeditor = CKEditor()
mail = Mail()
oauth = OAuth()

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    ckeditor.init_app(app)
    mail.init_app(app)
    oauth.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app
