import unittest
from app import create_app, db
from app.models import QuoteRequests, User, JobData
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        e = User(email='ralphpisner@email.com')
        e.set_password('cat')
        self.assertFalse(e.check_password('dog'))
        self.assertTrue(e.check_password('cat'))