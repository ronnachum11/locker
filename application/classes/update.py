from os import urandom 
import pymongo
from bson import ObjectId

from application import db

class Update:
    def __init__(self, id:str, version:str, date:str, name:str, headline:str, updates:list, coming_soon:list):
        self.id = str(id)
        self.version = version
        self.date = date
        self.name = name
        self.headline = headline
        self.updates = updates 
        self.coming_soon = coming_soon

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(dictionary:dict):
        return Course(str(dictionary.get("id")),
                dictionary.get("version"),
                dictionary.get("date"),
                dictionary.get("name"),
                dictionary.get("headline"),
                dictionary.get("updates"),
                dictionary.get("coming_soon")
            )

    def add(self):
        db.updates.insert(self.to_dict())

    @staticmethod
    def get_most_recent():
        return db.updates.find_one({}, sort=[('_id', pymongo.DESCENDING)])

    def __repr__(self):
        return f"Update('{str(self.id)}', '{self.version}', '{self.date}')"