import os

basedir = os.path.abspath(os.path.dirname(__file__))

# system configurations
class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or '123456'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'beauty_care.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_USERNAME = ['Betty']
    CARER_USERNAME = []
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    MAIL_SERVER = 'smtp.sendgrid.net'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'apikey'
    MAIL_PASSWORD = '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'
    MAIL_DEFAULT_SENDER = ('Beauty Care', 'noreply@example.com')
