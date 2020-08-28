from flask import render_template, flash, request, url_for, redirect, abort, session, Markup
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

from application import app, bcrypt, db, mail, login_manager
from application.models import User, Class
from application.forms.forms import ClassForm

import os 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/home", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("home.html")

@app.route("/login")
def login():
    user = User.query.first()
    login_user(user)
    print(current_user)
    return redirect(url_for('home'))

@app.route("/add_class")
@login_required
def add_class():
    form = ClassForm()
    if form.validate_on_submit():
        flash('Class Added Succsesfully!')
        redirect(url_for('home'))
    return render_template('add_class.html', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))