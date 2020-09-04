from flask import Flask
import os
from os import path
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from dotenv import load_dotenv

from application.classes.db import DB
from config import load_config

oauth_register, oauth_login = load_config("DEBUG")

app = Flask(__name__)   

db = DB(os.environ["MONGO_CONNECTION_STRING"])

Bootstrap(app)

app.config['SECRET_KEY'] = "5791628bb0b13ce0c676dfde281ba245"

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True

app.config['MAIL_USERNAME'] = os.environ["EMAIL_USER"]
app.config['MAIL_PASSWORD'] = os.environ["EMAIL_PASS"]

mail = Mail(app)

app.config['TEMPLATES_AUTO_RELOAD'] = True

from application.routes import main_routes
from application.routes import user_routes
from application.routes import class_routes
from application.routes import handlers