from flask import render_template, flash, request, url_for, redirect, abort, session, Markup
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from application import app, bcrypt, mail, login_manager
from application.classes.user import User
from application.classes.course import Course
from application.forms.forms import ClassForm, LoginForm, RegistrationForm, RegistrationIonForm, ImportClassesForm

from application.classes.course import Course 
from application.classes.user import User

import os 
import json 
import re

## Routes in this file
# /home
# /classroom

with open(os.path.join('application', 'tj.json')) as f:
    tj_json = json.load(f)

@app.route("/home", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def home():
    if not current_user.is_authenticated:
        return render_template("home.html")
    courses = current_user.courses
    if courses:
        courses = sorted(courses, key=lambda course: course.period)
        courses = [(c, list(set(c.times.keys())), list(set(c.times.values()))) for c in courses]
        courses = [(c, f"{days[0]}s and {days[1]}s, {times[0]}") if len(days) != 0 and len(times) != 0 else (c, "") for c, days, times in courses]
    else:
        courses = []
    text = "Choose a class or add a new one to get started."
    name=current_user.name
    
    return render_template("home.html", classes=courses, name=name, text=text, current_class="")

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

    courses = current_user.courses
    if courses:
        courses = sorted(courses, key=lambda course: course.period)
        courses = [(c, list(set(c.times.keys())), list(set(c.times.values()))) for c in courses]
        courses = [(c, f"{days[0]}s and {days[1]}s, {times[0]}") if len(days) != 0 and len(times) != 0 else (c, "") for c, days, times in courses]
    else:
        courses = []
    return render_template("home.html", classes=courses, name=name, text=text, error=error, current_class=current_link)
