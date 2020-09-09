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
                            times=None, teacher=form.teacher.data, user_id=current_user.id, desktop_alert_time=int(form.desktop_reminder.data))
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
                            times=times, teacher=form.teacher.data, user_id=current_user.id, custom_times=True, desktop_alert_time=int(form.desktop_reminder.data))
        current_user.add_course(course)
        flash('Class Added Successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_class.html', header="Add A Class", custom_time=False, update_class=False, color_list=color_list, period_list=period_list, has_email = current_user.email is not None, has_phone=current_user.phone is not None and current_user.carrier is not None, display_custom_div="none", display_class_1="none", display_class_2="none", display_class_3="none", custom_color="none", form=form)

@app.route("/import_classes", methods=["GET", "POST"])
def import_classes():
    form = ImportClassesForm()
    return render_template("import_classes.html", form=form)

@app.route("/update_class/<string:course_id>", methods=["GET", "POST"])
@login_required
def update_class(course_id):    
    course = current_user.get_course_by_id(course_id)
    weekdays = ["Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "Sun"]
    if course is None:
        abort(404)
    
    form = ClassForm()
    color = course.color if course.color in [i[0] for i in form.color.choices] else "custom"

    data = [[None for i in range(5)] for a in range(3)]

    if not course.times:
        form = ClassForm(name=course.name, teacher=course.teacher, link=course.link, custom_time=course.custom_times,
                        period=course.period, color=color, desktop_reminder=course.desktop_alert_time)
    else:
        for i, day in enumerate(course.times):
            data[i][0] = day
            hours_minutes = course.times[day]["start"].split(":")
            data[i][1] = hours_minutes[0]
            data[i][2] = hours_minutes[1] if len(hours_minutes[1]) == 2 else " " + hours_minutes[1]
            hours_minutes = course.times[day]["end"].split(":")
            data[i][3] = hours_minutes[0]
            data[i][4] = hours_minutes[1] if len(hours_minutes[1]) == 2 else " " + hours_minutes[1]
        form = ClassForm(name=course.name, teacher=course.teacher, link=course.link, custom_time=course.custom_times,
                     period=course.period, color=color, desktop_reminder=course.desktop_alert_time, number_of_classes = len(course.times),
                     day1=data[0][0], hour1=data[0][1], minute1=data[0][2], hour1End=data[0][3], minute1End=data[0][4],
                     day2=data[1][0], hour2=data[1][1], minute2=data[1][2], hour2End=data[1][3], minute2End=data[1][4],
                     day3=data[2][0], hour3=data[2][1], minute3=data[2][2], hour3End=data[2][3], minute3End=data[2][4])
    color_list, period_list = get_color_period_list(form)
    
    display_custom_div = "block" if course.custom_times else "none"
    display_class_1 = "block" if not course.custom_times or len(course.times) >= 1 else "none"
    display_class_2 = "block" if course.custom_times and len(course.times) >= 2 else "none"
    display_class_3 = "block" if course.custom_times and len(course.times) >= 3 else "none"
    custom_color = "none" if color != "custom" else "block"

    if form.validate_on_submit():
        times = dict()
        color = form.color.data 
        if color == "custom":
            color = form.custom_color.data.hex

        if not form.custom_time.data:
            course = current_user.update_course(course.id, name=form.name.data, link=form.link.data, color=color, period=form.period.data,
                            custom_times=False, times=None, teacher=form.teacher.data, user_id=current_user.id, desktop_alert_time=int(form.desktop_reminder.data))
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
            course = current_user.update_course(course.id, name=form.name.data, link=form.link.data, color=color, period=form.period.data,
                            times=times, teacher=form.teacher.data, user_id=current_user.id, custom_times=True, desktop_alert_time=int(form.desktop_reminder.data))
      
        flash('Class Updated Successfully!', 'success')
        return redirect(url_for('dashboard'))

    form.submit.label.text = "Update Class"

    return render_template('add_class.html', header=f"{course.name} ({course.period})", custom_time=course.custom_times, course_id=course.id, update_class=True, color=course.color, period=course.period, color_list=color_list, period_list=period_list, has_email = current_user.email is not None, has_phone=current_user.phone is not None and current_user.carrier is not None, display_custom_div=display_custom_div, display_class_1=display_class_1, display_class_2=display_class_2, display_class_3=display_class_3, custom_color=custom_color, form=form)

@app.route("/delete_class/<string:course_id>", methods=["GET", "POST"])
@login_required
def delete_class(course_id):
    course = current_user.get_course_by_id(course_id)
    if course is None:
        abort(404)

    current_user.delete_course(course.id)
    flash('Class Deleted Successfully', 'success')
    return redirect(url_for('dashboard'))