from flask import render_template, flash, request, url_for, redirect, abort, session, Markup
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

from application import app, bcrypt, db, mail, login_manager
from application.models import User, Class
from application.forms.forms import ClassForm, LoginForm, RegistrationForm, RegistrationIonForm, ImportClassesForm

import os 
import json 
import re

## Routesin this file
# /add_class
# /import_classes
# /update_class
# /delete_class

with open(os.path.join('application', 'tj.json')) as f:
    tj_json = json.load(f)

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

@app.route("/import_classes", methods=["GET", "POST"])
def import_classes():
    form = ImportClassesForm()
    return render_template("import_classes.html", form=form)

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