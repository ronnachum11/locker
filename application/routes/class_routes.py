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
        color = form.color.data
        if color == "custom":
            color = form.custom_color.data.hex

        times = None
        links = None
        office_hours = None
        teacher_contact = None 

        if form.custom_time.data:
            times = dict()
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

        if form.additional_links.data:
            links = dict()
            if int(form.number_of_links.data) >= 1:
                if form.link_name1.data and form.link_name1.data.strip() != "" and form.link1.data and form.link1.data.strip() != "":
                    links[form.link_name1.data] = form.link1.data
            if int(form.number_of_links.data) >= 2:
                if form.link_name2.data and form.link_name2.data.strip() != "" and form.link2.data and form.link2.data.strip() != "":
                    links[form.link_name2.data] = form.link2.data
            if int(form.number_of_links.data) >= 3:
                if form.link_name3.data and form.link_name3.data.strip() != "" and form.link3.data and form.link3.data.strip() != "":
                    links[form.link_name3.data] = form.link3.data
            if int(form.number_of_links.data) >= 4:
                if form.link_name4.data and form.link_name4.data.strip() != "" and form.link4.data and form.link4.data.strip() != "":
                    links[form.link_name4.data] = form.link4.data
            if int(form.number_of_links.data) >= 5:
                if form.link_name5.data and form.link_name5.data.strip() != "" and form.link5.data and form.link5.data.strip() != "":
                    links[form.link_name5.data] = form.link5.data
            if len(links) == 0:
                links = None

        if form.office_hours.data:
            office_hours = dict()
            office_hours[form.office_day.data] = dict()
            office_hours[form.office_day.data]["start"] = form.office_hour.data + ":" + form.office_minute.data
            office_hours[form.office_day.data]["end"] = form.office_hourEnd.data + ":" + form.office_minuteEnd.data
     
        if form.teacher_contact.data and form.teacher_email.data is not None and form.teacher_email.data.strip() != "":
            teacher_contact = dict()
            teacher_contact['email'] = form.teacher_email.data

        course = Course(id=str(ObjectId()), name=form.name.data, link=form.link.data, color=color, 
                        period=form.period.data, teacher=form.teacher.data, user_id=current_user.id,
                        times=times, links=links, office_hours=office_hours, teacher_contact=teacher_contact,
                        custom_times = times is not None)
        current_user.add_course(course)

        flash('Class Added Successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_class.html', header="Add A Class", color_list=color_list, period_list=period_list, course=None, form=form)

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
    weekdays = ["Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "Sun"]

    form = ClassForm()  

    color_list, period_list = get_color_period_list(form)        
    
    if form.validate_on_submit():
        color = form.color.data
        if color == "custom":
            if form.custom_color.data is None:
                color = course.color
            else:
                color = form.custom_color.data.hex

        times = None
        links = None
        office_hours = None
        teacher_contact = None 

        if form.custom_time.data:
            times = dict()
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

        if form.additional_links.data:
            links = dict()
            if int(form.number_of_links.data) >= 1:
                if form.link_name1.data and form.link_name1.data.strip() != "" and form.link1.data and form.link1.data.strip() != "":
                    links[form.link_name1.data] = form.link1.data
            if int(form.number_of_links.data) >= 2:
                if form.link_name2.data and form.link_name2.data.strip() != "" and form.link2.data and form.link2.data.strip() != "":
                    links[form.link_name2.data] = form.link2.data
            if int(form.number_of_links.data) >= 3:
                if form.link_name3.data and form.link_name3.data.strip() != "" and form.link3.data and form.link3.data.strip() != "":
                    links[form.link_name3.data] = form.link3.data
            if int(form.number_of_links.data) >= 4:
                if form.link_name4.data and form.link_name4.data.strip() != "" and form.link4.data and form.link4.data.strip() != "":
                    links[form.link_name4.data] = form.link4.data
            if int(form.number_of_links.data) >= 5:
                if form.link_name5.data and form.link_name5.data.strip() != "" and form.link5.data and form.link5.data.strip() != "":
                    links[form.link_name5.data] = form.link5.data
            if len(links) == 0:
                links = None

        if form.office_hours.data:
            office_hours = dict()
            office_hours[form.office_day.data] = dict()
            office_hours[form.office_day.data]["start"] = form.office_hour.data + ":" + form.office_minute.data
            office_hours[form.office_day.data]["end"] = form.office_hourEnd.data + ":" + form.office_minuteEnd.data
     
        if form.teacher_contact.data and form.teacher_email.data is not None and form.teacher_email.data.strip() != "":
            teacher_contact = dict()
            teacher_contact['email'] = form.teacher_email.data

        current_user.update_course(course.id, name=form.name.data, link=form.link.data, color=color, 
                        period=form.period.data, teacher=form.teacher.data, user_id=current_user.id,
                        times=times, links=links, office_hours=office_hours, teacher_contact=teacher_contact,
                        custom_times = times is not None)

        flash('Class Updated Successfully!', 'success')
        return redirect(url_for('dashboard'))

    color = course.color if course.color in [i[0] for i in form.color.choices] else "custom"
    custom_color = None if course.color in [i[0] for i in form.color.choices] else course.color

    time_data = [[None for i in range(5)] for a in range(3)]
    link_data = [[None for a in range(2)] for b in range(5)]
    office_hour_data = [None for a in range(5)]
    email = None 

    if course.times:
        for i, day in enumerate(course.times):
            time_data[i][0] = day
            hours_minutes = course.times[day]["start"].split(":")
            time_data[i][1] = hours_minutes[0]
            time_data[i][2] = hours_minutes[1] if len(hours_minutes[1]) == 2 else " " + hours_minutes[1]
            hours_minutes = course.times[day]["end"].split(":")
            time_data[i][3] = hours_minutes[0]
            time_data[i][4] = hours_minutes[1] if len(hours_minutes[1]) == 2 else " " + hours_minutes[1]

    if course.links:
        for i, name in enumerate(course.links):
            link_data[i][0] = name
            link_data[i][1] = course.links[name]

    if course.office_hours:
        for day in course.office_hours:
            office_hour_data[0] = day
            hours_minutes = course.office_hours[day]["start"].split(":")
            office_hour_data[1] = hours_minutes[0]
            office_hour_data[2] = hours_minutes[1] if len(hours_minutes[1]) == 2 else " " + hours_minutes[1]
            hours_minutes = course.office_hours[day]["end"].split(":")
            office_hour_data[3] = hours_minutes[0]
            office_hour_data[4] = hours_minutes[1] if len(hours_minutes[1]) == 2 else " " + hours_minutes[1]

    if course.teacher_contact:
        email = course.teacher_contact["email"]

    number_of_classes = "1" if course.times is None or len(course.times) == 0 else str(len(course.times))
    number_of_links = "1" if course.links is None or len(course.links) == 0 else str(len(course.links))

    form = ClassForm(name=course.name, teacher=course.teacher, link=course.link, custom_time=course.custom_times, custom_color=custom_color,
                period=course.period, color=color, desktop_reminder=course.desktop_alert_time, number_of_classes = number_of_classes,
                day1=time_data[0][0], hour1=time_data[0][1], minute1=time_data[0][2], hour1End=time_data[0][3], minute1End=time_data[0][4],
                day2=time_data[1][0], hour2=time_data[1][1], minute2=time_data[1][2], hour2End=time_data[1][3], minute2End=time_data[1][4],
                day3=time_data[2][0], hour3=time_data[2][1], minute3=time_data[2][2], hour3End=time_data[2][3], minute3End=time_data[2][4], 
                link_name1=link_data[0][0], link1=link_data[0][1], link_name2=link_data[1][0], link2=link_data[1][1], 
                link_name3=link_data[2][0], link3=link_data[2][1], link_name4=link_data[3][0], link4=link_data[3][1], 
                link_name5=link_data[4][0], link5=link_data[4][1], number_of_links=number_of_links, 
                additional_links=course.links is not None and len(course.links) > 0, 
                teacher_contact = course.teacher_contact is not None, teacher_email = email,
                office_hours=course.office_hours is not None and len(course.office_hours) > 0, office_day=office_hour_data[0], office_hour=office_hour_data[1], 
                office_minute=office_hour_data[2], office_hourEnd=office_hour_data[3], office_minuteEnd=office_hour_data[4])
    form.submit.label.text = "Update Class"

    return render_template('add_class.html', header=f"{course.name} ({course.period})", course=course, color=color, period=course.period, update_class=True, color_list=color_list, period_list=period_list, form=form)

@app.route("/delete_class/<string:course_id>", methods=["GET", "POST"])
@login_required
def delete_class(course_id):
    course = current_user.get_course_by_id(course_id)
    if course is None:
        abort(404)

    current_user.delete_course(course.id)
    flash('Class Deleted Successfully', 'success')
    return redirect(url_for('dashboard'))