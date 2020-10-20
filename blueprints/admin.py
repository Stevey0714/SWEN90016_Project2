from flask import render_template, url_for, request, flash, redirect, Blueprint
from app.extensions import db
from app.models import User, Role
admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
def admin():
    admin = User.query.filter_by(role_id="3").first()
    return f'<h1>Admin: {admin.name}</h1>' \
           f'<h2>Role: {Role.query.filter_by(ID=admin.role_id).first().name}</h2>' \
           f'<h2>Email: {admin.email}</h2>' \
           f'<h2>Contact: {admin.contact}</h2>' \
           f'<h2>Address: {admin.address}</h2>' \
           f'<h2>Extra_info: {admin.extra_info}</h2>'
