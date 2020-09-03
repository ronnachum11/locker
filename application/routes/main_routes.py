from flask import render_template, flash, request, url_for, redirect, abort, session, Markup
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

from application import app, bcrypt, db, mail, login_manager, oauth
from application.models import User, Class
from application.forms.forms import ClassForm, LoginForm, RegistrationForm, PhoneForm, RegistrationIonForm, ImportClassesForm

import os 
import json 
import re

## Routes in this file
# /home
# /classroom

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
