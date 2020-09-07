from flask import render_template, flash, request, url_for, redirect, abort, session, Markup
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from application import app, bcrypt, mail, login_manager
from application.classes.user import User
from application.classes.course import Course
from application.forms.forms import ContactForm, ClassForm, LoginForm, RegistrationForm, LoginIonForm, ImportClassesForm

from application.classes.course import Course 
from application.classes.user import User
from application.utils import send_contact_email

import os 
import json 
import re

## Routes in this file
# /home
# /classroom

with open(os.path.join('application', 'tj_weekly_sched.json')) as f:
    tj = json.load(f)

@app.route("/home", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def home():
    form = ContactForm()
    if current_user.is_authenticated:
        form.name.data = current_user.name
        form.email.data = current_user.email

    if form.validate_on_submit():
        send_contact_email(form.name.data, form.email.data, form.subject.data, form.message.data)
        flash('Contact form submitted successfully, we appreciate your thoughts!', 'success')
    return render_template("home.html", form=form)

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    if not current_user.is_authenticated:
        return render_template("home.html")
    courses = current_user.courses
    if courses:
        courses = sorted(courses, key=lambda course: course.period)
        courses = [(c, tj[c.period]) for c in courses]
    else:
        courses = []
    text = "Choose a class or add a new one to get started."
    name=current_user.name
    
    return render_template("dashboard.html", classes=courses, name=name, text=text, current_class="")

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
        courses = [(c, tj[c.period]) for c in courses]
    else:
        courses = []
    return render_template("dashboard.html", classes=courses, name=name, text=text, error=error, current_class=current_link)
