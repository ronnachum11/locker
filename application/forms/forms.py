import phonenumbers
from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextField, TextAreaField, BooleanField, DateField, RadioField, SelectField, PasswordField
from wtforms.fields.html5 import DateField
from wtforms_components import ColorField, TimeField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, ValidationError
from application.classes.user import User

minute_choices = [('1', '1'), ('2', '2'), ('3', '3'), ('5', '5'), ('10', '10'), ('15', '15')]
minute_choices = [(x[0], x[1] + ' Minutes Before') if x[1] != '1' else (x[0], x[1] + ' Minute Before') for x in minute_choices]
minute_choices = [('-1', "None")] + minute_choices

# minute_choices = [('-1', "None"), ('10', "10 Minutes Before")]

carriers = [('@mms.att.net', 'AT&T'), ('@tmomail.net', 'T-Mobile'), 
            ('@vtext.com', 'Verizon'), ('@page.nextel.com', 'Sprint')]

carriers = [('-1', 'Carrier: None'), ('AT&T', 'AT&T'),
            ('T-Mobile', 'T-Mobile'), ('Verizon', 'Verizon'), ('Sprint', 'Sprint')]

weekdays = [('Mon', 'Monday'), ('Tues', 'Tuesday'), ('Wed', 'Wednesday'), ('Thurs', 'Thursday'), ('Fri', 'Friday'), ('Sat', 'Saturday'), ('Sun', 'Sunday')]
hours = ['6', '7', '8', '9', '10', '11', '12', '1', '2', '3', '4', '5']; hours = [(x, x) for x in hours]
minutes = ['00', '05', '10', '15', '20', '25', '30', '35', '40', '45', '50', '55']; minutes = [(x, x) for x in minutes]

states = ['VA']
countries = ['USA']

countries = ['Afghanistan', 'Aland Islands', 'Albania', 'Algeria', 'American Samoa', 'Andorra', 'Angola', 'Anguilla', 'Antarctica', 'Antigua and Barbuda', 'Argentina', 'Armenia', 'Aruba', 'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bermuda', 'Bhutan', 'Bolivia', 'Bonaire, Saint Eustatius and Saba ', 'Bosnia and Herzegovina', 'Botswana', 'Brazil', 'British Indian Ocean Territory', 'British Virgin Islands', 'Brunei', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Cambodia', 'Cameroon', 'Canada', 'Cape Verde', 'Cayman Islands', 'Central African Republic', 'Chad', 'Chile', 'China', 'Christmas Island', 'Cocos Islands', 'Colombia', 'Comoros', 'Cook Islands', 'Costa Rica', 'Croatia', 'Cuba', 'Curacao', 'Cyprus', 'Czech Republic', 'Democratic Republic of the Congo', 'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic', 'East Timor', 'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Ethiopia', 'Falkland Islands', 'Faroe Islands', 'Fiji', 'Finland', 'France', 'French Guiana', 'French Polynesia', 'French Southern Territories', 'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Gibraltar', 'Greece', 'Greenland', 'Grenada', 'Guadeloupe', 'Guam', 'Guatemala', 'Guernsey', 'Guinea', 'Guinea-Bissau', 'Guyana', 'Haiti', 'Honduras', 'Hong Kong', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland', 'Isle of Man', 'Israel', 'Italy', 'Ivory Coast', 'Jamaica', 'Japan', 'Jersey', 'Jordan', 'Kazakhstan', 'Kenya', 'Kiribati', 'Kuwait', 'Kyrgyzstan', 'Laos', 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Macao', 'Macedonia', 'Madagascar', 'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Martinique', 'Mauritania', 'Mauritius', 'Mayotte', 'Mexico', 'Micronesia', 'Moldova', 'Monaco', 'Mongolia', 'Montenegro', 'Montserrat', 'Morocco', 'Mozambique', 'Myanmar', 'Namibia', 'Nauru', 'Nepal', 'Netherlands', 'New Caledonia', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'Niue', 'Norfolk Island', 'North Korea', 'Northern Mariana Islands', 'Norway', 'Oman', 'Pakistan', 'Palau', 'Palestinian Territory', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Pitcairn', 'Poland', 'Portugal', 'Puerto Rico', 'Qatar', 'Republic of the Congo', 'Reunion', 'Romania', 'Russia', 'Rwanda', 'Saint Barthelemy', 'Saint Helena', 'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Martin', 'Saint Pierre and Miquelon', 'Saint Vincent and the Grenadines', 'Samoa', 'San Marino', 'Sao Tome and Principe', 'Saudi Arabia', 'Senegal', 'Serbia', 'Seychelles', 'Sierra Leone', 'Singapore', 'Sint Maarten', 'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia', 'South Africa', 'South Georgia and the South Sandwich Islands', 'South Korea', 'South Sudan', 'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'Svalbard and Jan Mayen', 'Swaziland', 'Sweden', 'Switzerland', 'Syria', 'Taiwan', 'Tajikistan', 'Tanzania', 'Thailand', 'Togo', 'Tokelau', 'Tonga', 'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkmenistan', 'Turks and Caicos Islands', 'Tuvalu', 'U.S. Virgin Islands', 'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'United States', 'United States Minor Outlying Islands', 'Uruguay', 'Uzbekistan', 'Vanuatu', 'Vatican', 'Venezuela', 'Vietnam', 'Wallis and Futuna', 'Western Sahara', 'Yemen', 'Zambia', 'Zimbabwe', 'Myanmar']
countries = [(x, x) if x != "United States" else ('USA', 'USA') for x in countries]
states = {"AL":"Alabama","AK":"Alaska","AZ":"Arizona","AR":"Arkansas","CA":"California","CO":"Colorado","CT":"Connecticut","DE":"Delaware","FL":"Florida","GA":"Georgia","HI":"Hawaii","ID":"Idaho","IL":"Illinois","IN":"Indiana","IA":"Iowa","KS":"Kansas","KY":"Kentucky","LA":"Louisiana","ME":"Maine","MD":"Maryland","MA":"Massachusetts","MI":"Michigan","MN":"Minnesota","MS":"Mississippi","MO":"Missouri","MT":"Montana","NE":"Nebraska","NV":"Nevada","NH":"New Hampshire","NJ":"New Jersey","NM":"New Mexico","NY":"New York","NC":"North Carolina","ND":"North Dakota","OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania","RI":"Rhode Island","SC":"South Carolina","SD":"South Dakota","TN":"Tennessee","TX":"Texas","UT":"Utah","VT":"Vermont","VA":"Virginia","WA":"Washington","WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming"}
states = [(states[state], state) for state in states]

class ClassForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    teacher = StringField('Teacher', validators=[])
    link = StringField('Link', validators=[DataRequired()])
    color = RadioField('Color', validators=[DataRequired()], 
        choices=[('red', 'Red'), ('orange', 'Orange'), ('yellow', 'Yellow'), ('lime', 'Lime'), 
                 ('green', 'Green'), ('deepskyblue', 'Light Blue'), ('blue', 'Blue'),
                 ('hotpink', 'Pink'),('purple', 'Purple'), ('black', 'Black'), ('custom', 'Custom')])
    custom_color = ColorField('Color', validators=[])
    period = RadioField('Times', validators=[DataRequired()],
        choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), 
                 ('7', '7'), ('8', '8'), ('8A', '8A'), ('8B', '8B'), ('Homeroom', 'HR')])
    
    custom_time = BooleanField('Custom Time', default=False)
    number_of_classes = SelectField('Number of Classes', choices=[('1', '1'), ('2', '2'), ('3', '3')])
    day1 = SelectField('First Day', choices=weekdays)
    hour1 = SelectField('Hour', choices=hours, default="10")
    hour1End = SelectField('Hour', choices=hours, default="12")
    minute1 = SelectField('Minute', choices=minutes, default="00")
    minute1End = SelectField('Minute', choices=minutes, default="00")
    day2 = SelectField('First Day', choices=weekdays, default="Tues")
    hour2 = SelectField('Hour', choices=hours, default="10")
    hour2End = SelectField('Hour', choices=hours, default="12")
    minute2 = SelectField('Minute', choices=minutes, default="00")
    minute2End = SelectField('Minute', choices=minutes, default="00")
    day3 = SelectField('First Day', choices=weekdays, default="Wed")
    hour3 = SelectField('Hour', choices=hours, default="10")
    hour3End = SelectField('Hour', choices=hours, default="12")
    minute3 = SelectField('Minute', choices=minutes, default="00")
    minute3End = SelectField('Minute', choices=minutes, default="00")

    office_hours = BooleanField('Office Hours', default=False)
    office_day = SelectField('Office Day', choices=weekdays, default="Mon")
    office_hour = SelectField('Hour', choices=hours, default="10")
    office_hourEnd = SelectField('Hour', choices=hours, default="12")
    office_minute = SelectField('Minute', choices=minutes, default="00")
    office_minuteEnd = SelectField('Minute', choices=minutes, default="00")

    teacher_contact = BooleanField('Teacher Contact Info', default=False)
    teacher_email = StringField('Email')

    additional_links = BooleanField('Additional Links', default=False)
    number_of_links = SelectField('Number of Links',choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')])
    link_name1 = StringField('Link Name 1')
    link1 = StringField('Link 1')
    link_name2 = StringField('Link Name 2')
    link2 = StringField('Link 2')
    link_name3 = StringField('Link Name 3')
    link3 = StringField('Link 3')
    link_name4 = StringField('Link Name 4')
    link4 = StringField('Link 4')
    link_name5 = StringField('Link Name 5')
    link5 = StringField('Link 5')

    # desktop_reminder = SelectField('Minutes Before', choices=minute_choices, default='-1')
    # auto_load_time = SelectField('Minutes Before', choices=minute_choices, default='-1')
    # notes = TextAreaField('Notes')
    submit = SubmitField('Add Class')

    def validate_link(self, link):
        if 'https://us.bbcollab.com/invite/' not in link.data and 'https://meet.google.com/' not in link.data and 'https://us04web.zoom.us' not in link.data:
            raise ValidationError('Invalid Link. Try right clicking the email link and then clicking "Copy Link Address"')

class AssignmentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    course = SelectField('Course', choices=[('-1', '-1')], validators=[DataRequired()])
    due_date = DateField('Due Date', validators=[DataRequired()]) #, format="%m/%d/%Y")
    due_time = TimeField('Time Due', validators=[DataRequired()], default=datetime.strptime("23:59:00", "%H:%M:%S"))
    notes = TextAreaField('Additional Info (Optional)')
    submit = SubmitField('Add Assignment')

class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=1, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone')
    carrier = SelectField('Carrier', choices=carriers, validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    tj_student = BooleanField('TJ Student', default=False)
    school_name = StringField('School Name')
    school_type = SelectField('School Type', choices=[('ES', 'ES (K-6)'), ('MS', 'MS (7-8)'), ('HS', 'HS (9-12)'), ('University', 'University'), ('Other', 'None of these')], default="HS")
    city = StringField('City')
    state = SelectField('State', choices=states, default="Virginia")
    country = SelectField('Country', choices=countries, default="USA")
    submit = SubmitField('Sign Up')

    def validate_location_info(self, tj_student, school_name, city, state, country):
        if not tj_student.data and (school_name.data is None or school_name.data.strip() == "" or city.data is None or city.data.strip() == "" or state.data is None or country.data is None):
            raise ValidationError('Please fill out all location information.')

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

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.get_by_email(email=email.data)
        if user is None:
            raise ValidationError('There is no account with that email. Please create an account first.')
    
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

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