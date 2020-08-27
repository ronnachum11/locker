from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextField, TextAreaField, PasswordField, BooleanField, ColorField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class RegisterForm(FlaskForm):
    email = TextField('Email Address', [DataRequired()])
    password = PasswordField('Password', [DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password')
    submit = SubmitField('Register')
    # accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice (updated Jan 22, 2015)', [validators.Required()])

class LoginForm(FlaskForm):
    email = TextField('Email Address', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])

class ClassForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    link = StringField('Link', validators=[DataRequired()])
    color = ColorFIeld('Color', validators=[DataRequired()])
    times = StringField('Times', validators=[DataRequired()])
    teacher = StringField('Teacher', validators=[])
    notes = TextAreaField('Notes', validators=[])
    submit = SubmitField('Add Class')


