from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, AnonymousUserMixin

db = SQLAlchemy()
login_manager = LoginManager()


@login_manager.user_loader
def load_user(id):
    from app.models import User
    return User.query.get(int(id))


login_manager.login_view = ''  # 此处输入登陆界面的地址 e.g. admin.login
login_manager.login_message_category = 'warning'


class AnonymousUser(AnonymousUserMixin):
    username = 'Anonymous'
    role = ''

    def can(self, permissions):
        return False

    @property
    def is_admin(self):
        return False


login_manager.anonymous_user = AnonymousUser