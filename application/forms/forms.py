from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextField, TextAreaField, BooleanField, RadioField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp

minute_choices = [(1, '1'), (2, '2'), (3, '3'), (5, '5'), (10, '10'), 
                 (15, '15'), (20, '20'), (25, '25'), (30, '30')]
minute_choices = [(x[0], x[1] + ' Minutes Before') if x[1] != '1' else (x[0], x[1] + ' Minute Before') for x in minute_choices]

class ClassForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    link = StringField('Link', validators=[DataRequired(), Regexp('https://us.bbcollab.com/invite/*')])
    color = RadioField('Color', validators=[DataRequired()], 
        choices=[('red', 'Red'), ('orange', 'Orange'), ('yellow', 'Yellow'), ('lime', 'Lime'), 
                 ('green', 'Green'), ('deepskyblue', 'Light Blue'), ('blue', 'Blue'),
                 ('hotpink', 'Pink'),('purple', 'Purple')]) # , ('black', 'Black')])
    period = RadioField('Times', validators=[DataRequired()],
        choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'),
                 ('5', '5'), ('6', '6'), ('7', '7'), ('8A', '8A'), ('8B', '8B')])
    teacher = StringField('Teacher', validators=[])
    text_reminder = SelectField('Minutes Before', [], choices=minute_choices, default=5)
    email_reminder = SelectField('Minutes Before', [], choices=minute_choices, default=5)
    notes = TextAreaField('Notes', validators=[])
    submit = SubmitField('Add Class')

# class RegisterForm(FlaskForm):
#     email = TextField('Email Address', [DataRequired()])
#     password = PasswordField('Password', [DataRequired(), EqualTo('confirm', message='Passwords must match')])
#     confirm = PasswordField('Confirm Password')
#     submit = SubmitField('Register')
#     # accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice (updated Jan 22, 2015)', [validators.Required()])

# class LoginForm(FlaskForm):
#     email = TextField('Email Address', [DataRequired()])
#     password = PasswordField('Password', [DataRequired()])