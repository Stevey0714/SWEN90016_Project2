from app.extensions import db
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

'''
Different forms for database
'''

class Role(db.Model):
    __tablename__ = 'Role'
    ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.ORDER, True),
            'Carer': (Permission.VIEW_ORDER, False),
            'Admin': (Permission.VIEW_ORDER | Permission.ADD_SERVICE, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


class Permission:
    ORDER = 0x01
    VIEW_ORDER = 0x02
    ADD_SERVICE = 0x04


class Bill(db.Model):
    __tablename__ = 'Bill'
    ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('User.ID'))

    user = db.relationship('User', back_populates='bill')

    # def __repr__(self):
    #     return f"<{User.name}'s bill information: Biller Name: {self.name} \t E-mail: {self.email}>"

    # 输入用户ID，返回该用户所有的Bill Information
    def get_bill_info(self, ID):
        return Bill.query.filter_by(user_id=self.user_id).all()


class Service(db.Model):
    __tablename__ = 'Service'
    ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    rate = db.Column(db.Float(), nullable=False)
    add_by = db.Column(db.Integer, db.ForeignKey('User.ID'))

    user = db.relationship('User', back_populates='service')
    appointment = db.relationship('Appointment', back_populates='service')

    # def __repr__(self):
    #     return f'<{self.name}, charges {self.rate} per hour>'

    # 输入服务名称，返回该服务的信息
    def get_rate(self, service):
        return Service.query.filter_by(name=service).first()


class Appointment(db.Model):
    __tablename__ = 'Appointment'
    ID = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.Integer, db.ForeignKey('User.ID'))
    server = db.Column(db.Integer, db.ForeignKey('User.ID'))
    service_type = db.Column(db.Integer, db.ForeignKey('Service.ID'))
    time = db.Column(db.String(), nullable=False)
    date = db.Column(db.String(), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    message = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(10), nullable=False, default='Incomplete')

    custom = db.relationship('User', foreign_keys=[customer], back_populates='customer')
    serve = db.relationship('User', foreign_keys=[server], back_populates='server')
    service = db.relationship('Service', back_populates='appointment')


class User(UserMixin, db.Model):
    __tablename__ = 'User'
    ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True, nullable=False)
    email = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    contact = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    extra_info = db.Column(db.String(255), nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey('Role.ID'))

    bill = db.relationship('Bill', back_populates='user')
    service = db.relationship('Service', back_populates='user')
    customer = db.relationship('Appointment', foreign_keys=[Appointment.customer], back_populates='custom',
                               cascade='all')
    server = db.relationship('Appointment', foreign_keys=[Appointment.server], back_populates='serve',
                             cascade='all')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.name in current_app.config['CARER_USERNAME']:
                self.role = Role.query.filter_by(name='Carer').first()
            elif self.name in current_app.config['ADMIN_USERNAME']:
                self.role = Role.query.filter_by(name='Admin').first()
            else:
                self.role = Role.query.filter_by(default=True).first()

    # def __repr__(self):
    #     return f'<User {self.name}'

    def get_id(self):
        return str(self.ID)

    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_admin(self):
        return self.can(Permission.ADD_SERVICE)

    def is_carer(self):
        return self.can(Permission.VIEW_ORDER)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 返回该用户名是否被注册，如果已经注册则返回True，没有被注册则返回False
    def username_used(self, username):
        record = User.query.fileter_by(name=username).first()
        return record is not None
