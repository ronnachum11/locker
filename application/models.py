from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from application import db # , login_manager
from flask_login import UserMixin
from os import urandom
import copy

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    hex_id = db.Column(db.String, default=lambda: urandom(32).hex(), unique=True, nullable=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=True)
    password = db.Column(db.String, nullable=True)

    hasIon = db.Column(db.Boolean, nullable=False, default=False)
    hasGoogle = db.Column(db.Boolean, nullable=False, default=False)

    ion_oauth = db.Column(db.String, nullable=True)
    google_oauth = db.Column(db.String, nullable=True)

    classes = db.relationship('Class', backref='user', lazy=True)
    data = db.Column(db.JSON, nullable=True)

    def __repr__(self):
        return f"User('{str(self.id)}', '{self.email}', '{self.phone}')"

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hex_id = db.Column(db.String, default=lambda: urandom(32).hex(), unique=True, nullable=True)

    name = db.Column(db.String, nullable=False)
    link = db.Column(db.String, nullable=False)
    color = db.Column(db.String, nullable=False)
    period = db.Column(db.String, nullable=True)
    times = db.Column(db.JSON, nullable=False)
    teacher = db.Column(db.String, nullable=True)
    notes = db.Column(db.String, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    email_alert_time = db.Column(db.Integer, nullable=True)
    text_alert_time = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"Class('{str(self.id)}', '{self.name}', '{self.teacher}')"