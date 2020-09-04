from os import urandom
from bson import ObjectId
from flask_login import UserMixin

from application import db
from application.classes.course import Course


class User(UserMixin):
    def __init__(self, id:str=None, name:str=None, email:str=None, ion_id:int=None, phone:str=None, password:str=None, hasIon:bool=False, hasGoogle:bool=False, courses: [Course]=[], data:dict=None):
        self.id = id
        self.ion_id = ion_id
        self.name = name
        self.email = email
        self.phone = phone
        self.password = password

        self.hasIon = hasIon
        self.hasGoogle = hasGoogle

        self.courses = courses
        self.data = data

    def __repr__(self):
        return f"User('{str(self.id)}', '{self.email}', '{self.phone}')"
    
    def get_id(self):
        print(self.id)
        return self.id
    
    def to_dict(self):
        dictionary = self.__dict__
        return dictionary

    @staticmethod
    def from_dict(dictionary:dict):
        if dictionary == None:
            return None
        return User(str(dictionary.get("_id")),
                    dictionary.get('name'),
                    dictionary.get('email'),
                    dictionary.get('ion_id'),
                    dictionary.get('phone'),
                    dictionary.get('password'),
                    dictionary.get('hasIon'),
                    dictionary.get('hasGoogle'),
                    [Course.from_dict(course) for course in dictionary.get('courses')] if dictionary.get('courses') else None,
                    dictionary.get('data')
            )
    
    def add(self):
        db.users.insert(self.to_dict())
    
    @staticmethod
    def get_by_id(id: str):
        return User.from_dict(db.users.find_one({"_id": ObjectId(id)}))
    
    @staticmethod
    def get_by_ion_id(ion_id: str):
        return User.from_dict(db.users.find_one({"ion_id": ion_id}))

    @staticmethod
    def get_by_email(email: str):
        return User.from_dict(db.users.find_one({"email": email}))

    def add_course(self, course: Course):
        db.users.update({"_id": self.id}, {"$push": {"courses": course.to_dict()}})
    
    def delete_course(self, course_id: str):
        db.users.update({"_id": self.id}, {"$pull": {"courses": ObjectId(course_id)}})
    
    def update_course(self, course_id, **kwargs):
        for key, value in kwargs.items():
            db.users.update({"_id": self.id, "courses._id":ObjectId(course_id)}, {f"courses.{key}": value})

    def update_ion_status(self, status: bool):
        db.users.update({"_id": self.id}, {"hasIon": status})
    
    def update_password(self, password: str):
        db.users.update({"_id": self.id}, {"password": password})
    
    def update_ion_id(self, ion_id:str):
        db.users.update({"_id": self.id}, {"ion_id": ion_id})
    
    def update_phone(self, phone:str):
        db.users.update({"_id": self.id}, {"phone": phone})

