from flask import render_template, flash, request, url_for, redirect, abort, session, Markup
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from application import app, bcrypt, mail, login_manager

from application.classes.course import Course 
from application.classes.user import User
from application.classes.assignment import Assignment
from application.forms.forms import AssignmentForm

import os 
import json 
import re
from datetime import datetime 
from bson import ObjectId

## Routesin this file
# /add_assignment
# /update_assignment

@app.route("/add_assignment", methods=["GET", "POST"])
@login_required
def add_assignment():
    form = AssignmentForm()

    courses = sorted(current_user.courses, key = lambda x: x.period)
    choices = [(str(course.id), f"{str(course.name)} - {course.period}") for course in courses]
    form.course.choices = choices

    if form.validate_on_submit():
        a = Assignment(str(ObjectId()), form.name.data, form.course.data, 
                       datetime.combine(form.due_date.data, form.due_time.data), form.notes.data)
        current_user.add_assignment(a)
        flash('Assignment added successfuly', 'success')
        return redirect(url_for("dashboard"))

    return render_template('add_assignment.html', form=form, update=False)