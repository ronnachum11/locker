from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextField, TextAreaField, PasswordField, BooleanField, RadioField
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
    color = RadioField('Color', validators=[DataRequired()], 
        choices=[('red', 'Red'), ('orange', 'Orange'), ('yellow', 'Yellow'), ('lime', 'Lime'), 
                 ('green', 'Green'), ('deepskyblue', 'Light Blue'), ('blue', 'Blue'),
                 ('hotpink', 'Pink'),('purple', 'Purple')]) # , ('black', 'Black')])
    period = RadioField('Times', validators=[DataRequired()],
        choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'),
                 ('5', '5'), ('6', '6'), ('7', '7'), ('8A', '8A'), ('8B', '8B')])
    teacher = StringField('Teacher', validators=[])
    notes = TextAreaField('Notes', validators=[])
    submit = SubmitField('Add Class')


