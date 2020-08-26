from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from application import db # , login_manager
from flask_login import UserMixin
from os import urandom
import copy

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    hasIon = db.Column(db.Boolean, nullable=False)
    hasEmail = db.Column(db.Boolnea, nullable=False)
    email = db.Column(db.String, nullable=True)
    passowrd = db.Column(db.String, nullable=True)
    ion_oauth = db.Column(db.String, nullable=True)
    data = db.Column(db.JSON, nullable=True)

    def __repr__(self):
        return f"User('{str(self.id)}', '{self.email}')"

class Class(db.model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String, nullable=False)
    link = db.Column(db.String, nullable=False)
    times = db.Column(db.JSON, nullable=False)
    teacher = db.Column(db.String, nullable=True)
    notes = db.Column(db.String, nullable=True)

    email_alert_time = db.Column(db.Integer, nullable=True)
    text_alert_time = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"Class('{str(self.id)}', '{self.name}')"