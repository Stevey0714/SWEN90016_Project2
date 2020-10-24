from flask import render_template, url_for, request, flash, redirect, Blueprint
from app.extensions import db
from app.models import User, Role, Appointment, Service
from app.forms import LoginForm, RegisterForm, BookForm
from flask_login import login_user, login_required, current_user, logout_user
from flask_mail import Message
from app.decorators import permission_required, admin_required, user_required


admin_bp = Blueprint('admin', __name__)


@admin_bp.route("/Admin")
@login_required
@admin_required
def admin_page():
    user = current_user
    return render_template("Admin.html", user=user)

@admin_bp.route("/appointment_admin")
@login_required
@admin_required
def appointment_admin():
    # 从数据库拿所有的预约信息
    user = current_user
    appointments = []
    appointments += Appointment.query.filter_by(status='Incompleted')
    appointments += Appointment.query.filter_by(status='Cancelled')
    appointments += Appointment.query.filter_by(status='Completed')
    users_info = {user.ID: user for user in User.query.all()}
    services = {service.ID: service for service in Service.query.all()}
    return render_template("Appointment_admin.html", appointmentList=appointments, users_info=users_info,
                           services=services, user=user)

@admin_bp.route("/ServiceType", methods=["POST", "GET"])
@login_required
@admin_required
def service_type():
    # 从数据库拿所有的服务类型
    user = current_user
    services = Service.query.all()
    # typeList = ["hair cut", "hair wash and dry", "hair color"]
    return render_template("ServiceType.html", user=user, services=services)

@admin_bp.route("/AddService", methods=["POST", "GET"])
@login_required
@admin_required
def add_service():
    user = current_user
    if request.method == 'POST':
        service_type = request.form.get('type')
        rate = request.form.get('charge')
        if Service.query.filter_by(name=service_type).first():
            flash('Services already in database, please change another name')
            return redirect(url_for('admin.add_service'))
        new_service = Service(name=service_type, rate=rate, add_by=user.ID)
        db.session.add(new_service)
        db.session.commit()
        flash('Service add successfully!')
        return redirect(url_for('admin.service_type'))
    return render_template("AddService.html", user=user)
