from flask import render_template, flash, request, url_for, redirect, abort, session, Markup
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

from application import app, bcrypt, db, mail, login_manager
from application.models import User, Class
from application.forms.forms import ClassForm

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
    return render_template("home.html")

@app.route("/login")
def login():
    user = User.query.first()
    login_user(user)
    print(current_user)
    return redirect(url_for('home'))

@app.route("/add_class", methods=["GET", "POST"])
@login_required
def add_class():
    form = ClassForm()
    color_list, period_list = [], []
    for i, colors in enumerate(form.color.choices):
        color_list.append((f"color-{i}", colors[0], colors[1]))
    for i, periods in enumerate(form.period.choices):
        period_list.append((f"period-{i}", periods[0], periods[1]))

    print(form.validate_on_submit())
    if form.validate_on_submit():
        new_class = Class(name=form.name.data, link=form.link.data, color=form.color.data,
                          times=tj_json[form.period.data], teacher=form.teacher.data, user_id=current_user.id)
        db.session.add(new_class)
        db.session.commit()
        flash('Class Added Succsesfully!', 'success')
        return redirect(url_for('home'))

    return render_template('add_class.html', color_list=color_list, period_list=period_list, form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))