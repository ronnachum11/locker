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

def get_color_period_list(form):
    color_list, period_list = [], []
    for i, colors in enumerate(form.color.choices):
        color_list.append((f"color-{i}", colors[0], colors[1]))
    for i, periods in enumerate(form.period.choices):
        if not (current_user.school != "TJ" and (periods[0] == "8A" or periods[0] == "8B" or periods[0] == "Homeroom")) and not(current_user.school == "TJ" and periods[0] == "8"):
            period_list.append((f"period-{i}", periods[0], periods[1]))

    return color_list, period_list

@app.route("/add_class", methods=["GET", "POST"])
@login_required
def add_class():
    form = ClassForm()
    color_list, period_list = get_color_period_list(form)
    weekdays = ["Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "Sun"]

    if form.validate_on_submit():
        times = dict()
        color = form.color.data 
        if color == "custom":
            color = form.custom_color.data.hex

        if not form.custom_time.data:
            course = Course(id=str(ObjectId()), name=form.name.data, link=form.link.data, color=color, period=form.period.data,
                            times=None, teacher=form.teacher.data, user_id=current_user.id, desktop_alert_time=form.desktop_reminder.data)
        else:
            if int(form.number_of_classes.data) >= 1:
                times[form.day1.data] = dict()
                times[form.day1.data]["start"] = form.hour1.data + ":" + form.minute1.data
                times[form.day1.data]["end"] = form.hour1End.data + ":" + form.minute1End.data
            if int(form.number_of_classes.data) >= 2:
                times[form.day2.data] = dict()
                times[form.day2.data]["start"] = form.hour2.data + ":" + form.minute2.data
                times[form.day2.data]["end"] = form.hour2End.data + ":" + form.minute2End.data
            if int(form.number_of_classes.data) >= 3:
                times[form.day3.data] = dict()
                times[form.day3.data]["start"] = form.hour3.data + ":" + form.minute3.data
                times[form.day3.data]["end"] = form.hour3End.data + ":" + form.minute3End.data

            sorted(times, key=lambda x: weekdays.index(x))
            course = Course(id=str(ObjectId()), name=form.name.data, link=form.link.data, color=color, period=form.period.data,
                            times=times, teacher=form.teacher.data, user_id=current_user.id, custom_times=True, desktop_alert_time=form.desktop_reminder.data)
        current_user.add_course(course)
        flash('Class Added Successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_class.html', header="Add A Class", update_class=False, color_list=color_list, period_list=period_list, has_email = current_user.email is not None, has_phone=current_user.phone is not None and current_user.carrier is not None, form=form)

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
    color_list, period_list = get_color_period_list(form)
    
    if form.validate_on_submit():
        current_user.update_course(course_id, name=form.name.data, teacher=form.teacher.data,
                    link=form.link.data, period=form.period.data, color=form.color.data, times=None,
                    text_alert_time=int(form.text_reminder.data), email_alert_time=int(form.email_reminder.data))

        flash('Class Updated Successfully!', 'success')
        return redirect(url_for('dashboard'))

    form.submit.label.text = "Update Class"

    return render_template('add_class.html', header=f"{course.name} ({course.period})", course_id=course.id, update_class=True, color=course.color, period=course.period, color_list=color_list, period_list=period_list, has_email = current_user.email is not None, has_phone=current_user.phone is not None and current_user.carrier is not None, form=form)

@app.route("/delete_class/<string:course_id>", methods=["GET", "POST"])
@login_required
def delete_class(course_id):
    course = current_user.get_course_by_id(course_id)
    if course is None:
        abort(404)

    current_user.delete_course(course.id)
    flash('Class Deleted Successfully', 'success')
    return redirect(url_for('dashboard'))