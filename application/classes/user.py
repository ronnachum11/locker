from os import urandom
from bson import ObjectId

from application import db
from application.classes.course import Course


class User:
    def __init__(self, id:ObjectId, name:str, email:str, ion_id:int=None, phone:str=None, password:str=None, hasIon:bool=False, hasGoogle:bool=False, courses: [Course]=None, data:dict=None):
        self.id = str(id)
        self.ion_id = ion_id
        self.name = name
        self.email = email
        self.phone = phone
        self.password = password

        self.hasIon = hasIon
        self.hasGoogle = hasGoogle

        self.classes = classes
        self.data = data

    def __repr__(self):
        return f"User('{str(self.id)}', '{self.email}', '{self.phone}')"
    
    def to_dict(self):
        return self.__dict__
    
    @staticmethod
    def from_dict(dictionary:dict):
        return User(dictionary.get("id"),
                    dictionary.get('ion_id'),
                    dictionary.get('name'),
                    dictionary.get('email'),
                    dictionary.get('phone'),
                    dictionary.get('password'),
                    dictionary.get('hasIon'),
                    dictionary.get('hasGoogle'),
                    [Course.from_dict(course) for course in dictionary.get('courses')],
                    dictionary.get('data')
            )
    
    @staticmethod
    def get_by_id(id: ObjectId):
        return db.users.find({"_id": id})

    @staticmethod
    def get_by_email(email: str):
        return db.users.find({"email": email})

    def add_course(self, course: Course):
        db.users.update({"_id": self.id}, {"$push": {"courses": course.to_dict()}})
    
    def delete_course(self, course_id: ObjectId):
        db.users.update({"_id": self.id}, {"$pull": {"courses": course_id}})
    
    def update_course(self, course_id, **kwargs):
        for key, value in kwargs.items():
            db.users.update({"_id": self.id, "courses._id":course_id}, {f"courses.{key}": value})

    def update_ion_status(self, status: bool):
        db.users.update({"_id": self.id}, {"hasIon": status})
    
    def update_password(self, password: str):
        db.users.update({"_id": self.id}, {"password": password})

