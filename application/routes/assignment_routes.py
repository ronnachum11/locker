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

@app.route("/add_assignment", methods=["GET", "POST"], defaults={'close': False})
@app.route("/add_assignment/<close>", methods=["GET", "POST"])
@login_required
def add_assignment(close):
    form = AssignmentForm()

    courses = sorted(current_user.courses, key = lambda x: x.period)
    choices = [(str(course.id), f"{str(course.name)} - {course.period}") for course in courses]
    form.course.choices = choices

    if form.validate_on_submit():
        a = Assignment(str(ObjectId()), form.name.data, form.a_type.data, form.course.data, 
                       datetime.combine(form.due_date.data, form.due_time.data), form.notes.data)
        current_user.add_assignment(a)

        if close:
            return "<script>window.onload = window.close();</script>"

        flash('Assignment added successfuly', 'success')
        return redirect(url_for("dashboard"))

    return render_template('add_assignment.html', form=form, update=False, close=close)

@app.route("/update_assignment/<string:assignment_id>", methods=["GET", "POST"], defaults={'close': False})
@app.route("/update_assignment/<string:assignment_id>/<close>", methods=["GET", "POST"])
@login_required
def update_assignment(assignment_id, close):
    form = AssignmentForm()

    assignment = current_user.get_assignment_by_id(assignment_id)
    if not assignment:
        abort(404)

    form = AssignmentForm(name=assignment.name, course_id=assignment.course_id, due_date=assignment.due_date.date(),
            due_time=assignment.due_date.time(), notes=assignment.notes, a_type=assignment.a_type)

    form.submit.label.text = "Update Assignment"

    courses = sorted(current_user.courses, key = lambda x: x.period)
    choices = [(str(course.id), f"{str(course.name)} - {course.period}") for course in courses]
    form.course.choices = choices

    if form.validate_on_submit():
        current_user.update_assignment(assignment_id, name=form.name.data, a_type=form.a_type.data,
                                       course_id=form.course.data, notes=form.notes.data,
                                       due_date=datetime.combine(form.due_date.data, form.due_time.data))
        flash('Assignment updated successfuly', 'success')
        return redirect(url_for("dashboard"))

    form.course.data = assignment.course_id

    return render_template('add_assignment.html', form=form, update=True, assignment=assignment, close=close)

@app.route("/complete_assignment/<string:assignment_id>", methods=["POST"])
def complete_assignment(assignment_id):
    assignment = current_user.get_assignment_by_id(assignment_id)
    if not assignment:
        return {"Status": "Failure"}

    current_user.delete_assignment(assignment_id)
    current_user.increment_assignment_count()

    return {"Status": "Success"}

@app.route("/delete_assignment/<string:assignment_id>", methods=["POST"])
def delete_assignment(assignment_id):
    assignment = current_user.get_assignment_by_id(assignment_id)
    if not assignment:
        return {"Status": "Failure"}

    current_user.delete_assignment(assignment_id)

    return {"Status": "Success"}

@app.route("/get_assignments/<string:course>/<string:a_type>", methods=["GET"])
def get_assignments(course, a_type):
    assignments = [] if not current_user.assignments else current_user.assignments
    assignments = sorted(assignments, key=lambda x: x.due_date)
    assignments = [(a, current_user.get_course_by_id(a.course_id), a.due_date.strftime("%a, %m/%d/%y %I:%M %p")) for a in assignments]
    
    if course != "all":
        assignments = [a for a in assignments if a[0].course_id == course]
    if a_type != "all":
        assignments = [a for a in assignments if a[0].a_type == a_type]

    return render_template('assignments_update.html', assignments=assignments)