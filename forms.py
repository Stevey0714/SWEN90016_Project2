from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Email
from .models import User

'''
HTML forms 
'''


class LoginForm(FlaskForm):
    email = StringField('Email: ', validators=[DataRequired()])
    password = PasswordField('Password: ', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    email = StringField('Email Address: ', validators=[DataRequired(), Email()])
    username = StringField('User Name: ', validators=[DataRequired()])
    password = PasswordField('Password: ', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password: ', validators=[DataRequired(), EqualTo('password',
                                                                                               message='Two different passwords received, must be same.')])
    homeaddress = StringField('Home Address: ', validators=[DataRequired()])
    contactnumber = StringField('Contact Number: ', validators=[DataRequired()])
    extrainfo = StringField('Extra Info: ', validators=[])
    submit = SubmitField('Register Now')

    def validate_username(self, username):
        user = User.query.filter_by(name=username.data).first()
        if user is not None:
            # raise ValidationError("Username has already been registered, please choose another name.")
            return False
        else:
            return True

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email is not None:
            return False
        else:
            return True


class BookForm(FlaskForm):
    username = StringField('User Name', validators=[DataRequired()])
    servicetype = StringField('Service Type', validators=[DataRequired()])
    date = StringField('Date', validators=[DataRequired()])
    time = StringField('Time', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    optionalmassage = StringField('Optional Massage', validators=[DataRequired()])


class UpdatePersonForm(FlaskForm):
    email = StringField('Email Address: ', validators=[Email()])
    username = StringField('User Name: ', validators=[])
    password = PasswordField('Password: ', validators=[])
    confirm_password = PasswordField('Confirm Password: ', validators=[EqualTo('password', message='Two different passwords received, must be same.')])
    homeaddress = StringField('Home Address: ', validators=[])
    contactnumber = StringField('Contact Number: ', validators=[])
    extrainfo = StringField('Extra Info: ', validators=[])
    submit = SubmitField('Update')

    def validate_username(self, username):
        user = User.query.filter_by(name=username.data).first()
        if user is not None:
            # raise ValidationError("Username has already been registered, please choose another name.")
            return False
        else:
            return True
