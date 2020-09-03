from flask import render_template, flash, request, url_for, redirect, abort, session, Markup
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

from application import app, bcrypt, db, mail, login_manager, oauth
from application.models import User, Class
from application.forms.forms import ClassForm, LoginForm, RegistrationForm, PhoneForm, RegistrationIonForm

import os 
import json 
import re

with open(os.path.join('application', 'tj.json')) as f:
    tj_json = json.load(f)

@login_manager.user_loader
def load_user(user_id, is_ion=False):
    if not is_ion:
        return User.query.get(int(user_id))
    else:
        return User.query.filter_by(id=user_id).first()

@app.route("/home", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def home():
    if not current_user.is_authenticated:
        return render_template("home.html")
    classes = Class.query.filter_by(user_id=current_user.id).order_by(Class.period.desc()).all()[::-1]
    classes = [(c, list(set(c.times.keys())), list(set(c.times.values()))) for c in classes]
    classes = [(c, f"{days[0]}s and {days[1]}s, {times[0]}") if len(days) != 0 and len(times) != 0 else (c, "") for c, days, times in classes]
    text = "Choose a class or add a new one to get started."
    name=current_user.name
    
    return render_template("home.html", classes=classes, name=name, text=text, current_class="")

@app.route("/classroom/<string:hex_id>")
@login_required
def classroom(hex_id):
    current_class = Class.query.filter_by(hex_id=hex_id).all()

    current_link = ""
    if not current_user.is_authenticated:
        return redirect('home.html')
    
    if len(current_class) == 0:
        text = "The class you selected is invalid."
        error = "Error Code: 404"
    else:
        current_class = current_class[0]
        if current_class.user_id != current_user.id:
            text = "You are not authorized to access this class."
            error = "Error Code: 403"
        else:
            current_link = current_class.link
            text, error = "", ""
    name = current_user.name

    classes = Class.query.filter_by(user_id=current_user.id).order_by(Class.period.desc()).all()[::-1]
    classes = [(c, list(set(c.times.keys())), list(set(c.times.values()))) for c in classes]
    classes = [(c, f"{days[0]}s and {days[1]}s, {times[0]}") if len(days) != 0 and len(times) != 0 else (c, "") for c, days, times in classes]
    return render_template("home.html", classes=classes, name=name, text=text, error=error, current_class=current_link)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form1 = RegistrationForm()
    if form1.submit.data and form1.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form1.password.data).decode('utf-8')
        user = User(
            name=form1.name.data.title(), 
            email=form1.email.data,
            phone=form1.phone.data,
            password=hashed_pw
        )
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))

    form2 = RegistrationIonForm()
    if form2.submit2.data and form2.validate_on_submit():
        authorization_url, state = oauth.authorization_url("https://ion.tjhsst.edu/oauth/authorize/")
        return redirect(authorization_url)

    return render_template('register.html', title='Register', form1=form1, form2=form2)

@app.route("/register/ion", methods=["GET", "POST"])
def register_ion():
    try:
        token = oauth.fetch_token("https://ion.tjhsst.edu/oauth/token/",
                          code=request.args["code"],
                          client_secret="fTM1iaOIN1yBkoXGXuB9sBplIuYI5nJZCZZP22EpZgdDWoPvtFsTkAg7DNVxS6Jqc83GH1dpPXHAu2io2SdQr4naBbL2qedJiwsRIMdS9nJKlohvb24TvlyUj04vuPfs")
        profile = oauth.get("https://ion.tjhsst.edu/api/profile")
        profile = profile.json()
    except:
        pass
    
    if User.query.filter_by(id=profile["emails"][0]).first():
        flash("This account already exists with VirtuHall")
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
    
@login_required
@app.route("/add-phone-number", methods=["GET", "POST"])
def add_phone_number():
    form = PhoneForm()

    if form.validate_on_submit():
        user = User.query.filter_by(id=current_user.id).first()
        user.phone = re.sub("[^0-9]", "", form.phone.data)
        db.session.commit()
        flash("Phone number added")
        return redirect(url_for("home"))
    return render_template("register_ion.html", form=form)
    

@app.route("/backdoor_login")
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

    return render_template('add_class.html', header="Add A Class", update_class=False, color_list=color_list, period_list=period_list, has_email = current_user.email is not None, has_phone=current_user.phone is not None, form=form)

@app.route("/update_class/<string:hex_id>", methods=["GET", "POST"])
@login_required
def update_class(hex_id):    
    c = Class.query.filter_by(hex_id=hex_id).first_or_404()
    if current_user.id != c.user_id:
        abort(403)
    
    form = ClassForm(name=c.name, teacher=c.teacher, link=c.link, period=c.period, color=c.color,
                     text_reminder=c.text_alert_time, email_reminder=c.email_alert_time)
    color_list, period_list = [], []
    for i, colors in enumerate(form.color.choices):
        color_list.append((f"color-{i}", colors[0], colors[1]))
    for i, periods in enumerate(form.period.choices):
        period_list.append((f"period-{i}", periods[0], periods[1]))
    
    if form.validate_on_submit():
        c.name = form.name.data 
        c.teacher = form.teacher.data 
        c.link = form.link.data 
        c.period = form.period.data 
        c.color = form.color.data 
        c.text_alert_time = form.text_reminder.data 
        c.email_alert_time = form.email_reminder.data 
        c.times=tj_json[form.period.data]

        db.session.add(c)
        db.session.commit()
        flash('Class Update Successfully!', 'success')
        return redirect(url_for('home'))

    form.submit.label.text = "Update Class"

    return render_template('add_class.html', header=f"{c.name} ({c.period})", hex_id=c.hex_id, update_class=True, color=c.color, period=c.period, color_list=color_list, period_list=period_list, has_email = current_user.email is not None, has_phone=current_user.phone is not None, form=form)

@app.route("/delete_class/<string:hex_id>", methods=["GET", "POST"])
@login_required
def delete_class(hex_id):
    print('here')
    c = Class.query.filter_by(hex_id=hex_id).all()
    if len(c) == 0:
        abort(404)
    c = c[0]
    if current_user.id != c.user_id:
        abort(403)

    c = Class.query.filter_by(hex_id=hex_id).delete()
    db.session.commit()

    flash('Class Deleted Successfully', 'success')
    return redirect(url_for('home'))

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))