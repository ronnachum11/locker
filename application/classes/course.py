from os import urandom 
from bson import ObjectId

from application import db

class Course:
    def __init__(self, id:ObjectId, name:str, link:str, color:str, period:str, times:dict, teacher:str, user_id:ObjectId, email_alert_time:int, text_alert_time:int, data:dict):
        self.id = id

        self.name = name
        self.link = link
        self.color = color
        self.period = period
        self.times = times
        self.teacher = teacher
        self.user_id = user_id

        self.email_alert_time = email_alert_time
        self.text_alert_time = text_alert_time

        self.data = data

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(dictionary:dict):
        return Course(dictionary.get("id"),
                    dictionary.get("name"),
                    dictionary.get("link"),
                    dictionary.get("color"),
                    dictionary.get("period"),
                    dictionary.get("times"),
                    dictionary.get("teacher"),
                    dictionary.get("user_id"),
                    dictionary.get("email_alert_time"),
                    dictionary.get("text_alert_time"),
                    dictionary.get("data")
            )

    def __repr__(self):
        return f"Class('{str(self.id)}', '{self.name}', '{self.teacher}')"