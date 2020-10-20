from flask import render_template, url_for, request, flash, redirect, Blueprint
from app.models import User, Role
user_bp = Blueprint('user', __name__)


@user_bp.route('/user')
def user():
    users = User.query.filter_by(role_id='1').all()
    output = ''
    for user in users:
        output += f'<h1>Admin: {user.name}</h1>' \
           f'<h2>Role: {Role.query.filter_by(ID=user.role_id).first().name}</h2>' \
           f'<h2>Email: {user.email}</h2>' \
           f'<h2>Contact: {user.contact}</h2>' \
           f'<h2>Address: {user.address}</h2>' \
           f'<h2>Extra_info: {user.extra_info}</h2>'
    return output