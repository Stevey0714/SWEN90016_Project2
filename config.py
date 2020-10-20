import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or '123456'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'beauty_care.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_USERNAME = ['Betty']
    CARER_USERNAME = []
    BASEDIR = os.path.abspath(os.path.dirname(__file__))

