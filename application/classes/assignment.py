from os import urandom 
from bson import ObjectId

from application import db

class Assignment:
    def __init__(self, id:str, name:str, course_id:str, due_date:str, notes:str):
        self.id = str(id)

        self.name = name
        self.course_id = course_id 
        self.due_date = due_date
        self.notes = notes

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(dictionary:dict):
        return Assignment(str(dictionary.get("id")),
                    dictionary.get("name"),
                    dictionary.get("course_id"),
                    dictionary.get("due_date"),
                    dictionary.get("notes"),
            )

    def __repr__(self):
        return f"Assignment('{str(self.id)}', '{self.name}', '{self.due_date}')"