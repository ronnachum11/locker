from flask import render_template, flash, request, url_for, redirect, abort, session, Markup
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

from application import app, bcrypt, db, mail, login_manager
from application.models import User, Class
from application.forms.forms import ClassForm, LoginForm, RegistrationForm

import os 
import json 

with open(os.path.join('application', 'tj.json')) as f:
    tj_json = json.load(f)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/home", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def home():
    if not current_user.is_authenticated:
        return render_template("home.html")
    classes = Class.query.filter_by(user_id=current_user.id).order_by(Class.period.desc()).all()[::-1]
    classes = [(c, list(set(c.times.keys())), list(set(c.times.values()))) for c in classes]
    classes = [(c, f"{days[0]}s and {days[1]}s, {times[0]}") for c, days, times in classes]
    return render_template("home.html", classes=classes, name=current_user.name, current_class="")

@app.route("/classroom/<string:hex_id>")
def classroom(hex_id):
    current_class = Class.query.filter_by(hex_id=hex_id).first()
    if not current_user.is_authenticated or current_class.user_id != current_user.id:
        return render_template("home.html")
    classes = Class.query.filter_by(user_id=current_user.id).order_by(Class.period.desc()).all()[::-1]
    classes = [(c, list(set(c.times.keys())), list(set(c.times.values()))) for c in classes]
    classes = [(c, f"{days[0]}s and {days[1]}s, {times[0]}") for c, days, times in classes]
    return render_template("home.html", classes=classes, name=current_user.name, current_class=current_class.link)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            name=form.name.data.title(), 
            email=form.email.data,
            phone=form.phone.data,
            password=hashed_pw
        )
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/backdoor-login")
def backdoor_login():
    login_user(User.query.get(1))
    return redirect(url_for('home'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()

    if form.validate_on_submit():
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
    return render_template('login.html', title='Login', form=form)

@app.route("/add_class", methods=["GET", "POST"])
@login_required
def add_class():
    form = ClassForm()
    color_list, period_list = [], []
    for i, colors in enumerate(form.color.choices):
        color_list.append((f"color-{i}", colors[0], colors[1]))
    for i, periods in enumerate(form.period.choices):
        period_list.append((f"period-{i}", periods[0], periods[1]))

    if form.validate_on_submit():
        new_class = Class(name=form.name.data, link=form.link.data, color=form.color.data, period=form.period.data,
                          times=tj_json[form.period.data], teacher=form.teacher.data, user_id=current_user.id,
                          email_alert_time=form.email_reminder.data, text_alert_time=form.text_reminder.data)
        db.session.add(new_class)
        db.session.commit()
        flash('Class Added Succsesfully!', 'success')
        return redirect(url_for('home'))

    return render_template('add_class.html', color_list=color_list, period_list=period_list, has_email = current_user.email is not None, has_phone=current_user.phone is not None, form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))