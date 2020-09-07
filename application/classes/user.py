from os import urandom
from bson import ObjectId
from flask_login import UserMixin

from application import db
from application.classes.course import Course


class User(UserMixin):
    def __init__(self, id:str=None, name:str=None, email:str=None, ion_id:int=None, phone:str=None, carrier:str=None, password:str=None, school:str="TJ", hasIon:bool=False, hasGoogle:bool=False, courses: [Course]=[], data:dict=None):
        self.id = str(id)
        self.ion_id = ion_id
        self.name = name
        self.email = email
        self.phone = phone
        self.carrier = carrier
        self.password = password
        self.school = school

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
        dictionary = {
            "id": str(self.id),
            "name": self.name,
            "email": self.email,
            "ion_id": self.ion_id,
            "phone": self.phone,
            "carrier": self.carrier,
            "password": self.password,
            "school": self.school,
            "hasIon": self.hasIon,
            "hasGoogle": self.hasGoogle,
            "courses": [course.to_dict() for course in self.courses],
            "data": self.data
        }
        return dictionary

    @staticmethod
    def from_dict(dictionary:dict):
        if dictionary == None:
            return None
        user = User(str(dictionary.get("id")),
                    dictionary.get('name'),
                    dictionary.get('email'),
                    dictionary.get('ion_id'),
                    dictionary.get('phone'),
                    dictionary.get('carrier'),
                    dictionary.get('password'),
                    dictionary.get('school'),
                    dictionary.get('hasIon'),
                    dictionary.get('hasGoogle'),
                    [Course.from_dict(course) for course in dictionary.get('courses')] if dictionary.get('courses') else None,
                    dictionary.get('data')
            )
        return user
    
    def add(self):
        db.users.insert(self.to_dict())
    
    @staticmethod
    def get_by_id(id: str):
        return User.from_dict(db.users.find_one({"id": str(id)}))
    
    @staticmethod
    def get_by_ion_id(ion_id: str):
        print(ion_id)
        return User.from_dict(db.users.find_one({"ion_id": ion_id}))

    @staticmethod
    def get_by_email(email: str):
        return User.from_dict(db.users.find_one({"email": email}))

    def get_course_by_id(self, course_id: str):
        courses = [c for c in self.courses if c.id == course_id]
        return courses[0]

    def add_course(self, course: Course):
        db.users.update({"id": self.id}, {"$push": {"courses": course.to_dict()}})
    
    def delete_course(self, course_id: str):
        db.users.update({"id": self.id}, {"$pull": {"courses": {"id": course_id}}})
    
    def update_course(self, course_id, **kwargs):
        for key, value in kwargs.items():
            db.users.update({"id": self.id, "courses.id": course_id}, {"$set": {f"courses.$.{key}": value}})

    def update_ion_status(self, status: bool):
        db.users.update({"id": self.id}, {'$set' : {"hasIon":status}})
    
    def update_password(self, password: str):
        db.users.update({"id": self.id}, {'$set' : {"password":password}})
    
    def update_ion_id(self, ion_id:str):
        db.users.update({"id": self.id}, {'$set' : {"ion_id":ion_id}})

    def update_email(self, email:str):
        db.users.update({"id": self.id}, {'$set' : {"email":email}})

    def update_carrier(self, carrier:str):
        if carrier == "-1":
            carrier = None
        db.users.update({"id": self.id}, {'$set' : {"carrier":carrier}})

    def update_phone(self, phone:str):
        db.users.update({"id": self.id}, {'$set' : {"phone":phone}})

