from os import urandom
from bson import ObjectId
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from application import app, db
from application.classes.course import Course
from application.classes.assignment import Assignment

class User(UserMixin):
    def __init__(self, id:str=None, name:str=None, email:str=None, ion_id:int=None, phone:str=None, carrier:str=None, password:str=None, school:str="TJ", school_type:str="HS", city:str="Annandale", state:str="VA", country:str="USA", hasIon:bool=False, hasGoogle:bool=False, seen_recent_update:bool=False, _is_active:bool=False, courses: [Course]=[], data:dict=None, assignments: [Assignment]=[]):
        self.id = str(id)
        self.ion_id = ion_id
        self.name = name
        self.email = email
        self.phone = phone
        self.carrier = carrier
        self.password = password

        self.school = school
        self.school_type = school_type
        self.city = city
        self.state = state 
        self.country = country

        self.hasIon = hasIon
        self.hasGoogle = hasGoogle

        self.seen_recent_update = seen_recent_update
        self._is_active = _is_active

        self.courses = courses
        self.data = data
        self.assignments = assignments

    def __repr__(self):
        return f"User('{str(self.id)}', '{self.email}', '{self.phone}')"
    
    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, value):
        self._is_active = value
    
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
            "school_type": self.school_type,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "hasIon": self.hasIon,
            "hasGoogle": self.hasGoogle,
            "seen_recent_update": self.seen_recent_update,
            "is_active": self._is_active,
            "courses": [course.to_dict() for course in self.courses],
            "data": self.data,
            "assignments": [assignment.to_dict() for assignment in self.assignments]
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
                    dictionary.get('school_type'),
                    dictionary.get('city'),
                    dictionary.get('state'),
                    dictionary.get('country'),
                    dictionary.get('hasIon'),
                    dictionary.get('hasGoogle'),
                    dictionary.get('seen_recent_update'),
                    dictionary.get('is_active'), 
                    [Course.from_dict(course) for course in dictionary.get('courses')] if dictionary.get('courses') else None,
                    dictionary.get('data'),
                    [Assignment.from_dict(assignment) for assignment in dictionary.get('assignments')] if dictionary.get('assignments') else None
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
            db.users.update({"id": self.id, "courses.id": course_id}, {"$set": {f"courses.$.{key}": value}}, False, True)

    def get_assignment_by_id(self, assignment_id: str):
        courses = [a for a in self.assignments if a.id == assignment_id]
        return courses[0]

    def add_assignment(self, assignment: Assignment):
        db.users.update({"id": self.id}, {"$push": {"assignments": assignment.to_dict()}})
    
    def delete_assignment(self, assignment_id: str):
        db.users.update({"id": self.id}, {"$pull": {"assignments": {"id": assignment_id}}})
    
    def update_course(self, assignment_id, **kwargs):
        for key, value in kwargs.items():
            db.users.update({"id": self.id, "assignment.id": assignment_id}, {"$set": {f"assignment.$.{key}": value}}, False, True)

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
    
    def update_view_update(self, seen:bool):
        db.users.update({"id": self.id}, {'$set' : {"seen_recent_update":seen}})
    
    def update_is_active(self, active:bool):
        db.users.update({"id": self.id}, {'$set' : {"is_active":active}})
    
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.get_by_id(user_id)

    @staticmethod
    def get_total_users():
        return db.users.count() 

    @staticmethod
    def get_total_courses():
        lst = list(db.users.aggregate([{"$unwind": "$courses"}]))
        return len(lst)