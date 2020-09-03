from pymongo import MongoClient

from flask import current_app

class DB:
    def __init__(self, connection_string: str):
        self.db = MongoClient(connection_string).get_database("locker-database")

    def __repr__(self):
        return "<MongoDB database>"