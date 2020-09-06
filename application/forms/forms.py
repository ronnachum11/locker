import phonenumbers

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextField, TextAreaField, BooleanField, RadioField, SelectField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, ValidationError
from application.classes.user import User

minute_choices = [('1', '1'), ('2', '2'), ('3', '3'), ('5', '5'), ('10', '10'), 
                 ('15', '15'), ('20', '20'), ('25', '25'), ('30', '30')]
minute_choices = [(x[0], x[1] + ' Minutes Before') if x[1] != '1' else (x[0], x[1] + ' Minute Before') for x in minute_choices]
minute_choices = [('-1', "None")] + minute_choices

# minute_choices = [('-1', "None"), ('10', "10 Minutes Before")]

carriers = [('@mms.att.net', 'AT&T'), ('@tmomail.net', 'T-Mobile'), 
            ('@vtext.com', 'Verizon'), ('@page.nextel.com', 'Sprint')]

carriers = [('-1', 'No Carrier (Required for Text Reminders)'), ('AT&T', 'AT&T'),
            ('T-Mobile', 'T-Mobile'), ('Verizon', 'Verizon'), ('Sprint', 'Sprint')]

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
    text_reminder = SelectField('Minutes Before', validators=[DataRequired()], choices=minute_choices, default=-1)
    email_reminder = SelectField('Minutes Before', validators=[DataRequired()], choices=minute_choices, default=-1)
    notes = TextAreaField('Notes', validators=[])
    submit = SubmitField('Add Class')

    def validate_link(self, link):
        if not 'https://us.bbcollab.com/invite/' in link.data:
            raise ValidationError('Invalid Link. Try right clicking the email link and then clicking "Copy Link Address"')


class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=1, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone')
    carrier = SelectField('Carrier', choices=carriers, validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.get_by_email(email.data)
        if user:
            if user.password:
                raise ValidationError('This account has already been registered with The Locker.')
    
    def validate_password(self, email):
        user = User.get_by_email(email.data)
        if user and user.password is None:
            raise ValidationError('This account was created with ION, please register again to add a password.')
    
    def validate_phone(self, phone):
        if phone.data:
            if len(phone.data) > 16:
                raise ValidationError('Invalid phone number.')
            try:
                input_number = phonenumbers.parse(phone.data)
                if not (phonenumbers.is_valid_number(input_number)):
                    raise ValidationError('Invalid phone number.')
            except:
                input_number = phonenumbers.parse("+1"+phone.data)
                if not (phonenumbers.is_valid_number(input_number)):
                    raise ValidationError('Invalid phone number.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class LoginIonForm(FlaskForm):
    submit2 = SubmitField('Login With Ion')

class UpdatePhoneForm(FlaskForm):
    phone = StringField('Phone')
    carrier = SelectField('Carrier', choices=carriers, validators=[DataRequired()])
    submit = SubmitField('Update Phone')

    def validate_phone(self, field):
        if field:
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

class UpdateEmailForm(FlaskForm):
    email = StringField('Phone', validators=[Email()])
    submit = SubmitField('Update Email')


class ImportClassesForm(FlaskForm):
    text = TextAreaField('Email Text', validators=[DataRequired()])
    submit = SubmitField('Process Email')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Email')