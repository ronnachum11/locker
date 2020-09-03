from flask import Flask
import os
from os import path
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv

from application.classes.db import DB

load_dotenv(".env")

app = Flask(__name__)

db = DB(os.environ["MONGO_CONNECTION_STRING"])

Bootstrap(app)

app.config['SECRET_KEY'] = "5791628bb0b13ce0c676dfde281ba245"

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True

if path.exists(os.path.join('Website', 'application', 'environment_variables.txt')):
    f = open(os.path.join('Website', 'application', 'environment_variables.txt'), 'r')
else:
    pass 

app.config['MAIL_USERNAME'] = None
app.config['MAIL_PASSWORD'] = None

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

oauth_register = OAuth2Session("wpHYY2aXgZdm68bFj3h8QlG9mWPvb0Wwqvo2qPZF",
                      redirect_uri='http://127.0.0.1:5000/register/ion',
                      scope=["read","write"])

oauth_login = OAuth2Session("EDdTDiVb8gTQ34WGScGELsppMjI8S8w8MsSCphWu",
                      redirect_uri='http://127.0.0.1:5000/login/ion',
                      scope=["read","write"])

mail = Mail(app)

app.config['TEMPLATES_AUTO_RELOAD'] = True

from application.routes import main_routes
from application.routes import user_routes
from application.routes import class_routes
from application.routes import handlers