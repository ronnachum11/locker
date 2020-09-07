from flask import Flask
import os
from os import path
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from dotenv import load_dotenv

from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import requests
import json
import os
from datetime import datetime, timedelta

def get_tj_schedule():
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    periods = ["1", "2", "3", "4", "5", "6", "7", "8A", "8B", "Homeroom"]
    class_times = {course: "None" for course in periods}

    index = datetime.today().weekday()
    current_day = weekdays[index]

    if index <= 4:
        start, end = 0 - index, 5 - index
    else:
        start, end = 7 - index, 12 - index

    for num in range(start, end):
        day = datetime.today() + timedelta(days=num)
        date = day.strftime('%Y-%m-%d')
        weekday = weekdays[day.weekday()]
        data = requests.get(f"https://ion.tjhsst.edu/api/schedule/{date}").json()
        
        if 'blocks' in data['day_type']:
            for course in data['day_type']['blocks']:
                name = course['name'].replace("Period ", "")
                start_time = course['start'].replace("13:", "1:").replace("14:", "2:").replace("15:", "3:")
                if name in class_times:
                    if class_times[name] == "None":
                        class_times[name] = weekday + " @ " + start_time
                    else:
                        class_times[name] += ", " + weekday + " @ " + start_time

    print("Updated Class Times")

    with open(os.path.join('application', 'tj_weekly_sched.json'), 'w') as f:
        json.dump(class_times, f)

from application.classes.db import DB
from config import load_config

oauth_login = load_config()

app = Flask(__name__)   

db = DB(os.environ["MONGO_CONNECTION_STRING"])

Bootstrap(app)

app.config['SECRET_KEY'] = "5791628bb0b13ce0c676dfde281ba245"

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

scheduler = BackgroundScheduler()
scheduler.add_job(func=get_tj_schedule, trigger="interval", seconds=21600)
scheduler.start()

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

atexit.register(lambda: scheduler.shutdown())