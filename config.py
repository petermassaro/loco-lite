import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    QRS_PER_PAGE = 10

    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_NUMBER = '+16107238057'

    STRIPE_PUB_KEY = os.environ.get('STRIPE_PUB_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')

    ADMIN_EMAIL = ['pete@newtemphvac.com']
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['pete@newtemphvac.com']
    ADMIN_CELL = '6108126892'


    S3_ACCESS_KEY = os.environ.get('AWSAccessKeyId')
    S3_SECRET_KEY = os.environ.get('AWSSecretKey')
    S3_BUCKET = os.environ.get('S3_BUCKET')
    S3_PATH = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)