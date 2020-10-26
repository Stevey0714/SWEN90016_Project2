from flask import render_template, url_for, request, flash, redirect, Blueprint
from app.extensions import db
from app.models import User, Role, Bill, Service, Appointment
from app.forms import LoginForm, RegisterForm, BookForm, UpdatePersonForm
from flask_login import login_user, login_required, current_user, logout_user
import os
from app.config import Config
from werkzeug.urls import url_parse
from app.decorators import permission_required, admin_required, user_required
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Content, Mail, To, From
from threading import Thread

'''
User's pages 
'''

user_bp = Blueprint('user', __name__, url_prefix='', static_folder='../static')
sg = SendGridAPIClient(Config.MAIL_PASSWORD)


@user_bp.route('/')
@user_bp.route('/welcome')
def welcome():
    user = current_user
    return render_template('welcome.html', user=user)


@user_bp.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user.welcome'))
    form = RegisterForm()
    if form.validate_on_submit():
        if not form.validate_username(form.username):
            flash('Username has been registered, please choose another name.')
            return redirect(url_for('user.register'))
        if not form.validate_email(form.email):
            flash('Email has been registered, please choose another one.')
            return redirect(url_for('user.register'))
        register_user = User(name=str(form.username.data),
                             email=str(form.email.data),
                             contact=str(form.contactnumber.data),
                             address=str(form.homeaddress.data),
                             extra_info=str(form.extrainfo.data))
        register_user.set_password(form.password.data)
        db.session.add(register_user)
        db.session.commit()
        flash('Register Successfully!')
        # sending emails from verified email address
        sender = From('2371750502@qq.com')
        to = To(str(form.email.data))
        subject = "Welcome to Beauty Care!"
        content = Content('text/html', f'<b>Welcome! {form.username.data}</b>. <br> '
                                       f'<p>You have registered successfully in Beauty Health Care.</p>'
                                       f'<p>Looking forward to see you!</p>'
                                       f'<p>------</p>'
                                       f'<p>Best wishes,</p>'
                                       f'<p>Betty</p>')
        mail = Mail(from_email=sender, subject=subject, to_emails=to, html_content=content)
        thr = Thread(target=sg.client.mail.send.post, args=[mail.get()])
        thr.start()
        return redirect(url_for('user.register'))
    return render_template('register.html', form=form)


@user_bp.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user.appointment'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password, please try again')
            return redirect(url_for('user.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page):
            if current_user.role_id == 1:
                next_page = url_for('user.appointment')
            else:
                next_page = url_for('admin.admin_page')
        return redirect(next_page)
    return render_template('login.html', title="Sign In", form=form)


@user_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('user.welcome'))


@user_bp.route('/appointment')
@login_required
@user_required
def appointment():
    user = current_user.name
    return render_template('appointment.html', user=user)


@user_bp.route('/userinfo', methods=['POST', 'GET'])
@login_required
@user_required
def userinfo():
    user = current_user
    person_form = UpdatePersonForm()
    if request.method == "POST":
        if request.form.get('update'):
            original_ID = request.form.get('old_name')
            update_name = request.form.get('name')
            update_email = request.form.get('email')
            if original_ID != '':
                original_bill = Bill.query.filter_by(ID=original_ID).first()
                if update_name == original_bill.name and update_email == original_bill.email:
                    flash('Get same bill information, please modify the bill information for update')
                else:
                    original_bill.name = update_name
                    original_bill.email = update_email
                    db.session.commit()
                    flash('Update bill information successfully')
            else:
                new_biller = Bill(name=update_name, email=update_email, user_id=current_user.ID)
                db.session.add(new_biller)
                db.session.commit()
                flash('New biller information added')
            return redirect(url_for('user.userinfo'))
        elif request.form.get('delete'):
            original_ID = request.form.get('old_name')
            if original_ID != '':
                original_bill = Bill.query.filter_by(ID=original_ID).first()
                if original_bill:
                    db.session.delete(original_bill)
                    db.session.commit()
                    flash('Bill information removed')
                else:
                    flash('No biller information found, please check the biller information is entered correctly.')
            else:
                flash('No biller information found, please check the biller information is entered correctly.')
            return redirect(url_for('user.userinfo'))
    if person_form.validate_on_submit():
        if not person_form.validate_username(person_form.username) and user.name != person_form.username.data:
            flash('Username has been registered, please choose another name.')
            return redirect(url_for('user.userinfo'))
        flag = False
        if person_form.username.data and user.name != person_form.username.data:
            user.name = person_form.username.data
            flag = True
        if person_form.email.data and user.email != person_form.email.data:
            user.email = person_form.email.data
            flag = True
        if person_form.password.data and not user.check_password(person_form.password.data):
            user.set_password(person_form.password.data)
            flag = True
        if person_form.homeaddress.data and user.address != person_form.homeaddress.data:
            user.address = person_form.homeaddress.data
            flag = True
        if person_form.contactnumber.data and user.contact != person_form.contactnumber.data:
            user.contact = person_form.contactnumber.data
            flag = True
        if person_form.extrainfo.data and user.extra_info != person_form.extrainfo.data:
            user.extra_info = person_form.extrainfo.data
            flag = True
        db.session.commit()
        if flag:
            flash("Information updated successfully!")
        return redirect(url_for('user.userinfo'))
    current_biller = Bill.query.filter_by(user_id=current_user.ID).all()
    return render_template('userinfo.html', user=user, person_form=person_form, current_biller=current_biller)


@user_bp.route('/book', methods=['POST', 'GET'])
@login_required
@user_required
def book():
    user = current_user
    admin = User.query.filter_by(role_id=3).first()
    services = Service.query.all()
    expensive_service = max(services, key=lambda x: x.rate)
    booked_times = {}
    appointments = Appointment.query.filter_by(status='Incompleted')
    if appointments:
        for appointment in appointments:
            app_date = appointment.date
            app_time = appointment.time
            if app_date not in booked_times.keys():
                booked_times[app_date] = [app_time]
            else:
                booked_times[app_date] += [app_time]
    else:
        booked_times = None
    if request.method == "POST":
        service_type = request.form.get('servicetype')
        service_date = request.form.get('date')
        service_time = request.form.get('time')
        service_location = request.form.get('location')
        optional_message = request.form.get('optionalmessage')
        server_available = User.query.filter_by(role_id=3).first()
        customer = current_user
        service_ID = Service.query.filter_by(name=service_type).first().ID
        if service_time == 'Nothing':
            flash('Please select a valid time slot.')
            return redirect(url_for('user.book'))
        if booked_times:
            if service_date in booked_times.keys():
                if service_time in booked_times[service_date]:
                    flash('Sorry, the booked session has been taken, please choose another time slot.')
                    return redirect(url_for('user.book'))
        new_app = Appointment(customer=customer.ID, server=server_available.ID,
                              service_type=service_ID, time=service_time,
                              date=service_date, location=service_location,
                              message=optional_message, status='Incompleted')
        db.session.add(new_app)
        db.session.commit()
        flash('Booking successfully!')
        sender = From('2371750502@qq.com')
        to = To(str(current_user.email))
        subject = "New Booking with Beauty Care"
        content = Content('text/html', f'<b>Booking Success!</b>. <br> '
                                       f'<p>You have a new appointment of {service_type} with Beauty Care '
                                       f'at {service_date} {service_time}</p>'
                                       f'<p>Looking forward to see you there!</p>'
                                       f'<p>------</p>'
                                       f'<p>Best wishes,</p>'
                                       f'<p>Betty</p>')
        mail = Mail(from_email=sender, subject=subject, to_emails=to, html_content=content)
        thr = Thread(target=sg.client.mail.send.post, args=[mail.get()])
        thr.start()
        sender = From('2371750502@qq.com')
        to = To(str(admin.email))
        subject = "New Booking"
        content = Content('text/html', f'<b>New Appointment:</b>. <br> '
                                       f'<p><b>Service Type: </b>{service_type}</p>'
                                       f'<p><b>Location: </b>{service_location}</p>'
                                       f'<p><b>Customer Name: </b>{customer.name}</p>'
                                       f'<p><b>Time: </b>{service_date} {service_time}</p>'
                                       f'<p><b>Customer Phone Number: </b>{customer.contact}</p>'
                                       f'<p><b>Customer Email: </b>{customer.email}</p>'
                                       f'<p><b>Optional Message: </b>{optional_message}</p>'
                                       f'<p>------</p>'
                                       f'<p>Best,</p>'
                                       f'<p>Beauty Care Team</p>')
        mail = Mail(from_email=sender, subject=subject, to_emails=to, html_content=content)
        thr = Thread(target=sg.client.mail.send.post, args=[mail.get()])
        thr.start()
        return redirect(url_for('user.appointment'))
    return render_template('book.html', user=user, services=services, booked_times=booked_times,
                           expensive_service=expensive_service)


@user_bp.route('/booked', methods=['POST', 'GET'])
@login_required
@user_required
def booked():
    user = current_user
    admin = User.query.filter_by(role_id=3).first()
    appointments = Appointment.query.filter_by(customer=user.ID, status='Incompleted').order_by(Appointment.date,
                                                                                                Appointment.time).all()
    service_name = {service.ID: service.name for service in Service.query.all()}
    if request.method == 'POST':
        app_ID = request.form.get('app_ID')
        app = Appointment.query.filter_by(ID=app_ID).first()
        if app is not None:
            # Could just simply remove the record but not recommended
            # db.session.delete(app)
            app.status = 'Cancelled'
            db.session.commit()
            service_type = Service.query.filter_by(ID=app.service_type).first()
            service_location = app.location
            customer = User.query.filter_by(ID=app.customer).first()
            service_date = app.date
            service_time = app.time
            sender = From('2371750502@qq.com')
            to = To(str(admin.email))
            subject = "Appointment Cancelled"
            content = Content('text/html', f'<b>Appointment Cancelled:</b>. <br> '
                                           f'<p><b>Service Type: </b>{service_type}</p>'
                                           f'<p><b>Location: </b>{service_location}</p>'
                                           f'<p><b>Customer Name: </b>{customer.name}</p>'
                                           f'<p><b>Time: </b>{service_date} {service_time}</p>'
                                           f'<p><b>Customer Phone Number: </b>{customer.contact}</p>'
                                           f'<p><b>Customer Email: </b>{customer.email}</p>'
                                           f'<p>------</p>'
                                           f'<p>Best,</p>'
                                           f'<p>Beauty Care Team</p>')
            mail = Mail(from_email=sender, subject=subject, to_emails=to, html_content=content)
            thr = Thread(target=sg.client.mail.send.post, args=[mail.get()])
            thr.start()
            flash('Appointment cancel successfully!')
            return redirect(url_for('user.booked'))
        else:
            flash('No valid appointment found, please choose a valid appointment to cancel')
            return redirect(url_for('user.booked'))
    return render_template('booked.html', user=user, appointments=appointments, service_name=service_name)


@user_bp.route('/viewaptmt/<app_ID>', methods=["POST", "GET"])
@login_required
@user_required
def viewaptmt(app_ID):
    user = current_user
    appointment = Appointment.query.filter_by(ID=app_ID).first()
    service_name = {service.ID: service.name for service in Service.query.all()}
    if request.method == "POST":
        location = request.form.get('location')
        message = request.form.get('message')
        if location == appointment.location and message == appointment.message:
            flash('Fail to modify the appointment, same information received')
            return redirect(url_for('user.viewaptmt', app_ID=app_ID))
        elif location == '':
            flash('You cannot remove the location of service!')
            return redirect(url_for('user.viewaptmt', app_ID=app_ID))
        appointment.location = location
        appointment.message = message
        db.session.commit()
        flash('Modification has been record successfully!')
        return redirect(url_for('user.viewaptmt', app_ID=app_ID))
    return render_template('viewaptmt.html', user=user, appointment=appointment, service_name=service_name,
                           app_ID=app_ID)

# generating dynamic urls for fixing url updating issues
@user_bp.context_processor
def context_processor():
    def dated_url_for(endpoint, **values):
        if endpoint == 'static':
            filename = values.get('filename', None)
            if filename:
                file_path = os.path.join(Config.BASEDIR,
                                         endpoint, filename)
                values['q'] = int(os.stat(file_path).st_mtime)
        return url_for(endpoint, **values)

    return dict(url_for=dated_url_for)
