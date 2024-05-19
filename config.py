from os import environ

class Config(object):
    SQLALCHEMY_DATABASE_URI = f'postgresql://{environ.get('USER_USERNAME')}:{environ.get('USER_PASSWORD')}@localhost/flaskmpgu'
    SECRET_KEY = 'temp_key'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = environ.get('MAIL_PASSWORD')

class TestingConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f'postgresql://{environ.get('USER_USERNAME')}:{environ.get('USER_PASSWORD')}@localhost/flaskmpgutest'
    SECRET_KEY = 'temp_key'

