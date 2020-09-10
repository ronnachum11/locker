from os import urandom 
from bson import ObjectId

from application import db

class Course:
    def __init__(self, id:str, name:str, link:str, color:str, period:str, teacher:str, user_id:str, custom_times:bool=False, email_alert_time:int=-1, text_alert_time:int=-1, desktop_alert_time:int=-1, auto_load_time:int=-1, times:dict=None, links:dict=None, office_hours:dict=None, teacher_contact:dict=None, data:dict=None):
        self.id = str(id)

        self.name = name
        self.link = link
        self.color = color
        self.period = period
        self.times = times
        self.teacher = teacher
        self.user_id = user_id

        self.custom_times = custom_times
        self.links = links
        self.office_hours = office_hours
        self.teacher_contact = teacher_contact

        self.email_alert_time = int(email_alert_time)
        self.text_alert_time = int(text_alert_time)
        self.desktop_alert_time = int(desktop_alert_time)
        self.auto_load_time = int(auto_load_time)

        self.data = data

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(dictionary:dict):
        return Course(str(dictionary.get("id")),
                    dictionary.get("name"),
                    dictionary.get("link"),
                    dictionary.get("color"),
                    dictionary.get("period"),
                    dictionary.get("teacher"),
                    dictionary.get("user_id"),
                    dictionary.get("custom_times"),
                    int(dictionary.get("email_alert_time")),
                    int(dictionary.get("text_alert_time")),
                    int(dictionary.get("desktop_alert_time")),
                    int(dictionary.get("auto_load_time")),
                    dictionary.get("times"),
                    dictionary.get("links"),
                    dictionary.get("office_hours"),
                    dictionary.get("teacher_contact"),
                    dictionary.get("data")
            )

    def __repr__(self):
        return f"Course('{str(self.id)}', '{self.name}', '{self.teacher}')"