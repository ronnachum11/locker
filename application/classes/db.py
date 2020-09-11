from pymongo import MongoClient

from flask import current_app

class DB:
    def __init__(self, connection_string: str):
        self.db = MongoClient(connection_string).get_database("locker-database")
        self.users = self.db.users
        self.updates = self.db.updates

    def __repr__(self):
        return "<MongoDB database>"
    
    def update_seen_update(self):
        self.db.users.update_many({}, {"$set": {"seen_recent_update": False}})
