from flask import render_template, flash, request, url_for, redirect, abort, session, Markup
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

from application import app, bcrypt, mail, login_manager, oauth_login
from application.classes.user import User
from application.classes.course import Course
from application.forms.forms import ClassForm, LoginForm, RegistrationForm, UpdatePhoneForm, UpdateEmailForm, LoginIonForm, ImportClassesForm, LoginIonForm

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
    print(user_id, User.get_by_id(user_id))
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
            hashed_pw = bcrypt.generate_password_hash(form1.password.data).decode('utf-8')
            user = User(
                id=str(ObjectId()),
                name=form1.name.data.title(), 
                email=form1.email.data,
                phone=form1.phone.data,
                carrier=form1.carrier.data,
                password=hashed_pw
            )
            user.add()
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


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()

    if form.submit.data and form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user and user.password and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data, force=True)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('dashboard'))
            return redirect(url_for('dashboard'))
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
            hasIon=True
        )
        user.add()
        login_user(user, True)
        return redirect(url_for('account'))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))