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
from bson import ObjectId

## Routesin this file
# /add_assignment
# /update_assignment

@app.route("/add_assignment", methods=["GET", "POST"])
@login_required
def add_assignment():
    form = AssignmentForm()

    choices = [(str(course.id), str(course.name)) for course in current_user.courses]
    form.course.choices = choices

    if form.validate_on_submit():
        a = Assignment(str(ObjectId()), form.name.data, form.course.data, form.due_date.data, form.notes.data)

    return render_template('add_assignment.html', form=form, update=False)