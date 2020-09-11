from flask import render_template, flash, request, url_for, redirect, abort, session, Markup
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

from application import app, bcrypt, mail, login_manager, oauth_login
from application.classes.user import User
from application.classes.course import Course
from application.forms.forms import ClassForm, LoginForm, RegistrationForm, UpdatePhoneForm, UpdateEmailForm, LoginIonForm, RequestResetForm, ResetPasswordForm, ImportClassesForm, LoginIonForm

import os 
import json 
import re
from bson import ObjectId

## Routes in this file
# /resgister
# /register/ion
# /backdoor-login
# /account
# /add-phone-number
# /login
# /logout

@login_manager.user_loader
def load_user(user_id):
    user_id = str(user_id)
    return User.get_by_id(user_id)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form1 = RegistrationForm()
    if form1.submit.data and form1.validate_on_submit():
        if form1.carrier.data == "-1":
            form1.carrier.data = None
        user = User.get_by_email(form1.email.data)
        if user:
            if user.hasIon:
                user.update_password(bcrypt.generate_password_hash(form1.password.data).decode('utf-8'))
                user.update_phone(form1.phone.data)
                user.update_carrier(form1.carrier.data)
        else:
            if form1.tj_student.data:
                form1.school_name.data="TJ"
                form1.school_type.data="HS"
                form1.city.data="Annandale"
                form1.state.data="VA"
                form1.country.data="USA"

            hashed_pw = bcrypt.generate_password_hash(form1.password.data).decode('utf-8')
            user = User(
                id=str(ObjectId()),
                name=form1.name.data.title(), 
                email=form1.email.data,
                phone=form1.phone.data,
                carrier=form1.carrier.data,
                password=hashed_pw,
                school=form1.school_name.data,
                school_type=form1.school_type.data,
                city = form1.city.data,
                state = form1.state.data,
                country = form1.country.data,
                _is_active=False
            )
            flash("Your account has been created! Please check your email to verify your account.", "success")
            send_verification_email(user)
            user.add()
            return redirect(url_for('login'))
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))

    form2 = LoginIonForm()
    if form2.submit2.data and form2.validate_on_submit():
        authorization_url, state = oauth_login.authorization_url("https://ion.tjhsst.edu/oauth/authorize/")
        return redirect(authorization_url)

    return render_template('register.html', title='Register', form1=form1, form2=form2)

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    courses = current_user.courses
    if courses:
        courses = sorted(courses, key=lambda course: course.period)
    else:
        courses = []
    # course = courses[0]
    # print(course.email_alert_time, course.text_alert_time)
    has_phone = current_user.phone is not None
    return render_template('account.html', classes=courses, has_phone=has_phone, has_email=current_user.email is not None)

@login_required
@app.route("/update-phone", methods=["GET", "POST"])
def update_phone():
    form = UpdatePhoneForm()

    if form.validate_on_submit():
        current_user.update_phone(re.sub("[^0-9]", "", form.phone.data))
        current_user.update_carrier(form.carrier.data)
        flash("Phone number updated", 'success')
        return redirect(url_for("account"))

    if current_user.phone:
        form.phone.data = current_user.phone
    if current_user.carrier:
        form.carrier.data = current_user.carrier

    return render_template("update_phone.html", form=form)

@app.route("/update-email", methods=["GET", "POST"])
@login_required
def update_email():
    form = UpdateEmailForm()
    if current_user.email:
        form.email.data = current_user.email

    if form.validate_on_submit():
        current_user.update_email(form.email.data)
        flash("Email updated", 'success')
        return redirect(url_for("account"))
    return render_template("update_email.html", form=form)


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        send_reset_email(user)
        flash('An email has been sent to ' + form.email.data + ' to reset password', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()

    if form.submit.data and form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user and user.password and bcrypt.check_password_hash(user.password, form.password.data):
            if login_user(user, remember=form.remember.data):
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                else:
                    return redirect(url_for('dashboard'))
                return redirect(url_for('dashboard'))
            else:
                flash(f"Verify your account by checking the email sent to {form.email.data}", "danger")
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    form2 = LoginIonForm()

    if form2.submit2.data and form2.validate_on_submit():
        authorization_url, state = oauth_login.authorization_url("https://ion.tjhsst.edu/oauth/authorize/")
        return redirect(authorization_url)

    return render_template('login.html', title='Login', form=form, form2=form2)

@app.route("/ion", methods=["GET", "POST"])
def login_ion():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    try:
        token = oauth_login.fetch_token("https://ion.tjhsst.edu/oauth/token/",
                          code=request.args["code"],
                          client_secret=os.environ['LOGIN_CLIENT_SECRET'])
        profile = oauth_login.get("https://ion.tjhsst.edu/api/profile")
        profile = profile.json()
    except:
        flash('We had a problem authenticating your ion account. Please try again', 'danger')
        return redirect(url_for('home'))

    if profile['emails'] and len(profile['emails']) > 0 and User.get_by_email(profile['emails'][0]):
        login_user(User.get_by_email(profile['emails'][0]), True)
        return redirect(url_for('dashboard'))
    elif profile['id'] and User.get_by_ion_id(profile['id']):
        login_user(User.get_by_ion_id(profile['id']), True)
        return redirect(url_for('dashboard'))
    else:
        email = profile["emails"][0] if profile['emails'] and len(profile['emails']) > 0 else None
        user = User(
            id=str(ObjectId()),
            ion_id=profile["id"],
            name=profile["display_name"], 
            email=email,
            hasIon=True,
            _is_active=True
        )
        user.add()
        login_user(user, True)
        return redirect(url_for('account'))
    
@app.route("/verify_account/<token>", methods=['GET', 'POST'])
def verify_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('home'))
    
    user.update_is_active(True)
    flash('Your account has been activated!', 'success')
    return redirect(url_for('login'))

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('home'))
    
    form = ResetPasswordForm()

    if form.validate_on_submit():
        user.update_password(bcrypt.generate_password_hash(form.password.data))
        flash('Your password has been reset!', 'success')
        return redirect(url_for('login'))
    
    return render_template("reset_password.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

def send_verification_email(user: User):
    token = user.get_reset_token()
    msg = Message('Account Verification', sender='thelockerioapp@gmail.com', recipients=[user.email])
    msg.body = f'''To activate your account, visit the following link:
{url_for('reset_token', token=token, _external=True)}
'''
    mail.send(msg)

def send_reset_email(user: User):
    token = user.get_reset_token()
    msg = Message('Request Reset Password', sender='thelockerioapp@gmail.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
'''
    mail.send(msg)