from flask_migrate import Migrate
from config import Config
from browsers_app import create_app, db
import unittest
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from browsers_app.models import User, Post, Permission
from flask_login import current_user


class UserView(ModelView):
    """
    user view for flask-admin page
    list of displayed columns, 
    and who can access the page
    """
    column_display_pk = True
    column_list = ('id', 'username', 'email', 'date_added', 'confirmed',
                   'name', 'about', 'created_at', 'last_seen', 'role_id')

    def is_accessible(self):
        return current_user.is_authenticated and current_user.can(Permission.ADMIN)


class PostView(ModelView):
    """
    post view for flask-admin page
    """
    def is_accessible(self):
        return current_user.is_authenticated and current_user.can(Permission.ADMIN)


app = create_app(Config)
migrate = Migrate(app, db)
admin = Admin(app)
admin.add_view(UserView(User, db.session))
admin.add_view(PostView(Post, db.session))


@app.cli.command('test')
def test():
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

from errorRoutes import *
