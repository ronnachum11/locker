from flask import render_template, flash, request, url_for, redirect, abort, session, Markup
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

from application import app, bcrypt, db, mail, login_manager
from application.models import User, Class

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

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))