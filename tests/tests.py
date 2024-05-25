import unittest
from flask import current_app
from browsers_app import create_app, db
from config import TestingConfig
from browsers_app.models import User, Post, Permission, AnonUser, Role


class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exist(self):
        self.assertFalse(current_app is None)

    def test_app_isTesting(self):
        self.assertTrue(TestingConfig)

    def test_index(self):
        tester = self.app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_404(self):
        tester = self.app.test_client(self)
        response = tester.get('/nonexistent', content_type='html/text')
        self.assertEqual(response.status_code, 404)

    def test_user_model(self):
        u = User(username='test', email="i@i.ru")
        db.session.add(u)
        db.session.commit()
        u_from_db = User.query.filter_by(username='test').first()
        self.assertIsNotNone(u_from_db)
        self.assertEqual(u.username, 'test')

    def test_post_creation(self):
        with self.app.app_context():
            user = User(username='testuser', email='test@example.com')
            db.session.add(user)
            db.session.commit()

            post = Post(title='Test Post',
                        content='This is a test.', poster_id=user.id)
            db.session.add(post)
            db.session.commit()

            assert Post.query.count() == 1

    def test_user_role(self):
        Role.insert_roles()
        user = User(username='test', email="i@i.ru")
        self.assertTrue(user.can(Permission.COMMENT))
        self.assertTrue(user.can(Permission.FOLLOW))
        self.assertTrue(user.can(Permission.WRITE))
        self.assertFalse(user.can(Permission.MODERATE))
        self.assertFalse(user.can(Permission.ADMIN))

    def test_anon_user(self):
        Role.insert_roles()
        user = AnonUser()
        self.assertFalse(user.can(Permission.COMMENT))
        self.assertFalse(user.can(Permission.FOLLOW))
        self.assertFalse(user.can(Permission.WRITE))
        self.assertFalse(user.can(Permission.MODERATE))
        self.assertFalse(user.can(Permission.ADMIN))
