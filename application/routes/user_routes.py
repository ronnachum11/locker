from flask import render_template, flash, request, url_for, redirect, abort, session, Markup
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

from application import app, bcrypt, mail, login_manager, oauth_login
from application.classes.user import User
from application.classes.course import Course
from application.forms.forms import ClassForm, LoginForm, RegistrationForm, NewIonAccountForm, LoginIonForm, ImportClassesForm, LoginIonForm

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
        return redirect(url_for('home'))

    form1 = RegistrationForm()
    if form1.submit.data and form1.validate_on_submit():
        user = User.get_by_email(form1.email.data)
        if user:
            if user.hasIon:
                user.password = bcrypt.generate_password_hash(form1.password.data).decode('utf-8')
                user.update_password(user.password)
        else:
            hashed_pw = bcrypt.generate_password_hash(form1.password.data).decode('utf-8')
            user = User(
                id=str(ObjectId()),
                name=form1.name.data.title(), 
                email=form1.email.data,
                phone=form1.phone.data,
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

@login_required
@app.route("/account", methods=["GET", "POST"])
def account():
    courses = current_user.courses
    if courses:
        courses = sorted(courses, key=lambda course: course.period)
    else:
        courses = []
    # course = courses[0]
    # print(course.email_alert_time, course.text_alert_time)
    has_phone = current_user.phone is not None
    return render_template('account.html', classes=courses, has_phone=has_phone)

@login_required
@app.route("/add-phone-number", methods=["GET", "POST"])
def add_phone_number():
    form = NewIonAccountForm()

    if form.validate_on_submit():
        current_user.update_phone(re.sub("[^0-9]", "", form.phone.data))
        flash("Phone number added", 'success')
        return redirect(url_for("dashboard"))
    return render_template("register_ion.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()

    if form.submit.data and form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user and user.password and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data, force=True)
            next_page = request.args.get('next')
            if next_page:
                return redirect(url_for(next_page))
            else:
                return redirect(url_for('home'))
            return redirect(url_for('home'))
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
        return redirect(url_for('home'))

    try:
        token = oauth_login.fetch_token("https://ion.tjhsst.edu/oauth/token/",
                          code=request.args["code"],
                          client_secret=os.environ['LOGIN_CLIENT_SECRET'])
        profile = oauth_login.get("https://ion.tjhsst.edu/api/profile")
        profile = profile.json()
    except:
        pass

    if User.get_by_email(profile['emails'][0]):
        login_user(User.get_by_email(profile['emails'][0]), True)
        return redirect(url_for('dashboard'))
    else:
        user = User(
            id=str(ObjectId()),
            ion_id=profile["id"],
            name=profile["display_name"], 
            email=profile["emails"][0],
            hasIon=True
        )
        user.add()
        login_user(user, True)
        return redirect(url_for('add_phone_number'))

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))