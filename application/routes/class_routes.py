from flask import render_template, flash, request, url_for, redirect, abort, session, Markup
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

from application import app, bcrypt, mail, login_manager
from application.classes.user import User
from application.classes.course import Course
from application.forms.forms import ClassForm, LoginForm, RegistrationForm, LoginIonForm, ImportClassesForm

from application.classes.course import Course 
from application.classes.user import User

import os 
import json 
import re
from bson import ObjectId

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
        course = Course(id=str(ObjectId()), name=form.name.data, link=form.link.data, color=form.color.data, period=form.period.data,
                          times=tj_json[form.period.data], teacher=form.teacher.data, user_id=current_user.id,
                          email_alert_time=form.email_reminder.data, text_alert_time=form.text_reminder.data)
        current_user.add_course(course)
        flash('Class Added Successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('add_class.html', header="Add A Class", update_class=False, color_list=color_list, period_list=period_list, has_email = current_user.email is not None, has_phone=current_user.phone is not None, form=form)

@app.route("/import_classes", methods=["GET", "POST"])
def import_classes():
    form = ImportClassesForm()
    return render_template("import_classes.html", form=form)

@app.route("/update_class/<string:course_id>", methods=["GET", "POST"])
@login_required
def update_class(course_id):    
    course = current_user.get_course_by_id(course_id)
    if course is None:
        abort(404)
    
    form = ClassForm(name=course.name, teacher=course.teacher, link=course.link,
                     period=course.period, color=course.color, text_reminder=course.text_alert_time, 
                     email_reminder=course.email_alert_time)
    color_list, period_list = [], []
    for i, colors in enumerate(form.color.choices):
        color_list.append((f"color-{i}", colors[0], colors[1]))
    for i, periods in enumerate(form.period.choices):
        period_list.append((f"period-{i}", periods[0], periods[1]))
    
    if form.validate_on_submit():
        current_user.update_course(course_id, name=form.name.data, teacher=form.teacher.data,
                    link=form.link.data, period=form.period.data, color=form.color.data, 
                    text_alert_time=form.text_reminder.data, email_alert_time=form.email_reminder.data, 
                    times=dict(tj_json[form.period.data]))

        flash('Class Updated Successfully!', 'success')
        return redirect(url_for('home'))

    form.submit.label.text = "Update Class"

    return render_template('add_class.html', header=f"{course.name} ({course.period})", course_id=course.id, update_class=True, color=course.color, period=course.period, color_list=color_list, period_list=period_list, has_email = current_user.email is not None, has_phone=current_user.phone is not None, form=form)

@app.route("/delete_class/<string:course_id>", methods=["GET", "POST"])
@login_required
def delete_class(course_id):
    course = current_user.get_course_by_id(course_id)
    if course is None:
        abort(404)

    current_user.delete_course(course.id)
    flash('Class Deleted Successfully', 'success')
    return redirect(url_for('home'))