from app.extensions import db
from app.models import User
from faker import Faker

fake = Faker()


def fake_admin():
    admin = User(name='Betty', email='1234567890@gmail.com',
                 contact='+1234567890', address='No. 123, 4th street, 567, 890')
    admin.set_password('123456789')
    db.session.add(admin)
    db.session.commit()


def fake_user(count=10):
    for i in range(count):
        user = User(name=fake.name(), email=fake.email(),
                    contact=fake.msisdn(), address=fake.address())
        user.set_password('123456789')
        db.session.add(user)
        db.session.commit()
