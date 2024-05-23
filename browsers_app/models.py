from flask_login import UserMixin, AnonymousUserMixin
from . import login_manager
from . import db
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.jose import JsonWebSignature
from os import environ

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16

class Role(db.Model):
    # __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0


    def __repr__(self):
        return "Role: %r" % self.name
    
    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE],
            'Admin': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE, Permission.ADMIN]
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permission()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()
    
    def has_permission(self, perm):
        return self.permissions & perm == perm

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permission(self):
        self.permissions = 0

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    password_hash = db.Column(db.String(128))
    posts = db.relationship("Post", backref="poster")
    confirmed = db.Column(db.Boolean(), default=False)
    name = db.Column(db.String(64))
    about = db.Column(db.Text())
    created_at = db.Column(db.DateTime(), default=datetime.utcnow())
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow())
    role_id=db.Column(db.Integer, db.ForeignKey("role.id"))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            # if self.email == app.config['MAIL_USERNAME']:
            if self.email == environ.get("ADMIN_MAIL"):
                self.role = Role.query.filter_by(name='Admin').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)
    
    def is_admin(self):
        return self.can(Permission.ADMIN)

    def generate_confirmation_token(self, expiration=3600):
        jws = JsonWebSignature()
        protected = {"alg": "HS256"}
        payload = self.id
        secret = 'SECRET_KEY'
        return jws.serialize_compact(protected=protected, payload=payload, key=secret)

    def confirm(self, token):
        jws = JsonWebSignature()
        trimmed_token = token[2:]
        data = jws.deserialize_compact(s=trimmed_token, key='SECRET_KEY')
        if data.payload.decode('utf-8') != str(self.id):
            print("Not your token")
            return False
        else:
            self.confirmed = True
            db.session.add(self)
            return True

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    @property
    def password(self):
        raise AttributeError("property is not readable")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password, "pbkdf2")

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return "Name: password.getter%r" % self.username
    
class AnonUser(AnonymousUserMixin):
    def can(self, perm):
        return False
    def is_admin(self):
        return False

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    content = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(256))
    poster_id = db.Column(db.Integer, db.ForeignKey("user.id"))

login_manager.anonymous_user = AnonUser