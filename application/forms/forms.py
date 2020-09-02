import phonenumbers

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextField, TextAreaField, BooleanField, RadioField, SelectField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, ValidationError
from application.models import User

minute_choices = [(1, '1'), (2, '2'), (3, '3'), (5, '5'), (10, '10'), 
                 (15, '15'), (20, '20'), (25, '25'), (30, '30')]
minute_choices = [(x[0], x[1] + ' Minutes Before') if x[1] != '1' else (x[0], x[1] + ' Minute Before') for x in minute_choices]
minute_choices = [(-1, "None")] + minute_choices

# minute_choices = [(-1, "None"), (10, "10 Minutes Before")]

class ClassForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    link = StringField('Link', validators=[DataRequired(), Regexp('https://us.bbcollab.com/invite/*')])
    color = RadioField('Color', validators=[DataRequired()], 
        choices=[('red', 'Red'), ('orange', 'Orange'), ('yellow', 'Yellow'), ('lime', 'Lime'), 
                 ('green', 'Green'), ('deepskyblue', 'Light Blue'), ('blue', 'Blue'),
                 ('hotpink', 'Pink'),('purple', 'Purple'), ('black', 'Black')])
    period = RadioField('Times', validators=[DataRequired()],
        choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), 
                 ('7', '7'), ('8A', '8A'), ('8B', '8B'), ('Homeroom', 'HR')])
    teacher = StringField('Teacher', validators=[])
    text_reminder = SelectField('Minutes Before', [], choices=minute_choices, default=-1)
    email_reminder = SelectField('Minutes Before', [], choices=minute_choices, default=-1)
    notes = TextAreaField('Notes', validators=[])
    submit = SubmitField('Add Class')

class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone')
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email has already been registered with vTJ.')
    
    def validate_phone(self, field):
        if len(field.data) > 16:
            raise ValidationError('Invalid phone number.')
        try:
            input_number = phonenumbers.parse(field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('Invalid phone number.')
        except:
            input_number = phonenumbers.parse("+1"+field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('Invalid phone number.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class PhoneForm(FlaskForm):
    phone = StringField('Phone')
    submit = SubmitField('Add')

    def validate_phone(self, field):
        if len(field.data) > 16:
            raise ValidationError('Invalid phone number.')
        try:
            input_number = phonenumbers.parse(field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('Invalid phone number.')
        except:
            input_number = phonenumbers.parse("+1"+field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('Invalid phone number.')

class RegistrationIonForm(FlaskForm):
    submit2 = SubmitField('Register With Ion')