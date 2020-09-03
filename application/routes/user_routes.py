from flask import render_template, flash, request, url_for, redirect, abort, session, Markup
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

from application import app, bcrypt, db, mail, login_manager, oauth_register, oauth_login
from application.forms.forms import ClassForm, LoginForm, RegistrationForm, NewIonAccountForm, RegistrationIonForm, ImportClassesForm, LoginIonForm

from application.classes.course import Course 
from application.classes.user import User

import os 
import json 
import re

## Routes in this file
# /resgister
# /register/ion
# /backdoor-login
# /account
# /add-phone-number
# /login
# /logout

@login_manager.user_loader
def load_user(user_id, is_ion=False):
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
                name=form1.name.data.title(), 
                email=form1.email.data,
                phone=form1.phone.data,
                password=hashed_pw
            )
            user.add()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))

    form2 = RegistrationIonForm()
    if form2.submit2.data and form2.validate_on_submit():
        authorization_url, state = oauth_register.authorization_url("https://ion.tjhsst.edu/oauth/authorize/")
        return redirect(authorization_url)

    return render_template('register.html', title='Register', form1=form1, form2=form2)

@app.route("/register/ion", methods=["GET", "POST"])
def register_ion():
    try:
        token = oauth_register.fetch_token("https://ion.tjhsst.edu/oauth/token/",
                          code=request.args["code"],
                          client_secret="fTM1iaOIN1yBkoXGXuB9sBplIuYI5nJZCZZP22EpZgdDWoPvtFsTkAg7DNVxS6Jqc83GH1dpPXHAu2io2SdQr4naBbL2qedJiwsRIMdS9nJKlohvb24TvlyUj04vuPfs")
        profile = oauth_register.get("https://ion.tjhsst.edu/api/profile")
        profile = profile.json()
    except:
        pass

    if User.get_by_ion_id(profile['ion_id']):
        flash('ION Account already exists with The Locker', 'danger')
        return redirect(url_for('home'))     
    
    temp_user = User.get_by_email(profile['emails'][0])
    if temp_user:
        temp_user.ion_id = profile["id"]
        temp_user.hasIon = True
        db.session.commit()
        flash("Account updated with ION info", 'success')
        return redirect(url_for("home"))

    user = User(
        id=profile["id"],
        name=profile["display_name"], 
        email=profile["emails"][0],
        hasIon=True
    )
    login_user(user, True)
    db.session.add(user)
    db.session.commit()
    
    return redirect(url_for('add_phone_number'))
    
@app.route("/backdoor-login")
def backdoor_login():
    user = User.query.filter_by(hasIon=True).first()
    login_user(user)
    return redirect(url_for('home'))

@login_required
@app.route("/account", methods=["GET", "POST"])
def account():
    print(current_user.is_authenticated)
    classes = Class.query.filter_by(user_id=current_user.id).order_by(Class.period.desc()).all()[::-1]
    has_phone = current_user.phone is not None
    return render_template('account.html', classes=classes, has_phone=has_phone)

@login_required
@app.route("/add-phone-number", methods=["GET", "POST"])
def add_phone_number():
    form = NewIonAccountForm()

    if form.validate_on_submit():
        user = User.query.filter_by(id=current_user.id).first()
        user.phone = re.sub("[^0-9]", "", form.phone.data)
        db.session.commit()
        flash("Phone number and pasword added", 'success')
        return redirect(url_for("home"))
    return render_template("register_ion.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()

    if form.submit.data and form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
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

@app.route("/login/ion", methods=["GET", "POST"])
def login_ion():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    try:
        token = oauth_login.fetch_token("https://ion.tjhsst.edu/oauth/token/",
                          code=request.args["code"],
                          client_secret="PBNhfEPj2N2d4johiJ0p3pDTVZUAE1gbiBZw9JpnXuAJAqvYvLmWOB6bMilEtp9udTRUm9fY5KzwfzPkg1rYCkR1LSOKLKUBfI2EcOvNmnQbat9lTxeZNcg7JGM9sEiu")
        profile = oauth_login.get("https://ion.tjhsst.edu/api/profile")
        profile = profile.json()
    except:
        pass

    if User.query.filter_by(email=profile["emails"][0]).first():
        login_user(User.query.filter_by(email=profile["emails"][0]).first())
        return redirect(url_for('home'))
    else:
        return redirect(url_for('register'))

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))