from flask import render_template, flash, request, url_for, redirect, abort, session, Markup
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from application import app, bcrypt, mail, login_manager
from application.classes.user import User
from application.classes.course import Course
from application.forms.forms import ContactForm, ClassForm, LoginForm, RegistrationForm, LoginIonForm, ImportClassesForm

from application.classes.course import Course 
from application.classes.user import User
from application.classes.update import Update
from application.utils import send_contact_email

import os 
import json 
import re

## Routes in this file
# /home
# /classroom

with open(os.path.join('application', 'tj.json')) as f:
    tj = json.load(f)

with open(os.path.join('application', 'fcps_hs.json')) as f:
    fcps_hs = json.load(f)

with open(os.path.join('application', 'fcps_ms.json')) as f:
    fcps_ms = json.load(f)

def get_courses_and_strings():
    school_to_times = {"TJ": tj, "FCPS HS": fcps_hs, "FCPS MS": fcps_ms}
    courses = current_user.courses
    if courses:
        courses = sorted(courses, key=lambda course: course.period)
        strings = []
        for course in courses:
            if course.custom_times:
                times = course.times
                string = ""
                for i, day in enumerate(times):
                    if i == 0:
                        string += day + " " + times[day]["start"] + "-" + times[day]["end"]
                    else:
                        string += ", " + day + " " + times[day]["start"] + "-" + times[day]["end"]
                strings.append(string)
            elif current_user.school in school_to_times:
                times = school_to_times[current_user.school][course.period]
                string = ""
                for i, day in enumerate(times):
                    if i == 0:
                        string += day + " " + times[day]["start"] + "-" + times[day]["end"]
                    else:
                        string += ", " + day + " " + times[day]["start"] + "-" + times[day]["end"]
                strings.append(string)
            else:
                strings.append("None")
        courses = [(courses[i], strings[i]) for i in range(len(courses))]
    else:
        courses = []
    return courses

def check_recent_update():
    if current_user.is_authenticated:
        if not current_user.seen_recent_update:
            seen_recent_update = False
            update = Update.get_most_recent()
            current_user.update_view_update(True)
            return(update)
    return None

@app.route("/home", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def home():
    form = ContactForm()
    if current_user.is_authenticated:
        form.name.data = current_user.name
        form.email.data = current_user.email

    update = check_recent_update()

    total_users = User.get_total_users()
    total_courses = User.get_total_courses()

    if form.validate_on_submit():
        send_contact_email(form.name.data, form.email.data, form.subject.data, form.message.data)
        flash('Contact form submitted successfully, we appreciate your thoughts!', 'success')
    return render_template("home.html", form=form, update=update, total_users=total_users, total_courses=total_courses)

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    if not current_user.is_authenticated:
        return render_template("home.html")

    update = check_recent_update()

    courses = get_courses_and_strings()
    text = "Choose a class or add a new one to get started."
    name=current_user.name

    seen_recent_update = check_recent_update()
    
    return render_template("dashboard.html", classes=courses, name=name, text=text, current_class="", update=update)

@app.route("/classroom/<string:course_id>")
@login_required
def classroom(course_id):
    if not current_user.is_authenticated:
        abort(403)

    current_course = current_user.get_course_by_id(course_id)
    
    if current_course is None:
        text = "The class you selected is invalid."
        error = "Error Code: 404"
    else:
        current_link = current_course.link
        text, error = "", ""
    name = current_user.name

    courses = get_courses_and_strings()
    for i, course in enumerate(courses):
        if course[0] == current_course:
            current_course_info = course 
            courses.pop(i)
            break
    courses = [current_course_info] + courses

    return render_template("dashboard.html", classes=courses, name=name, text=text, error=error, current_class=current_link)

@app.route("/privacy_policy")
def privacy_policy():
    return render_template("privacy_policy.html")