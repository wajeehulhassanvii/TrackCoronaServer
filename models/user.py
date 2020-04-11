import os
from extensions import db
from extensions import bcrypt

from flask_login import UserMixin
from flask_bcrypt import check_password_hash
from sqlalchemy import func

import datetime as dt
from binascii import hexlify
from werkzeug import security


class User(UserMixin, db.Model):
    """Simple database model to track event attendees."""
    __name__ = 'User'
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    # , index=True, autoincrement=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    phone_number = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    creation_time = db.Column(db.DateTime, nullable=True,
                              server_default=func.now())
    modification_time = db.Column(db.DateTime, nullable=True,
                                  onupdate=func.now())
    active = db.Column(db.Boolean, default=True)

    user_health = db.relationship('UserHealth',
                                  backref='the_person',
                                  uselist=False)
    user_last_location = db.relationship('LastLocationPostGis',
                                         backref='the_person',
                                         uselist=False)

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "password": self.password,
            "phone_number": self.phone_number,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "active": self.active
                }

    def __init__(self,
                 email=None,
                 password=None,
                 phoneNumber=None,
                 firstName=None,
                 lastName=None
                 ):
        self.email = email,
        self.password = password,
        self.phone_number = phoneNumber,
        self.first_name = firstName,
        self.last_name = lastName,
        self.active = True
        # self.is_authenticated = True
        # self.creation_time = dt.datetime.utcnow
        # self.creation_time = timezone('utc', now())
        print(db.session.query(func.count(User.id)).scalar())
        self.id = db.session.query(func.count(User.id)).scalar() + 1

    def set_password(self, password):
        """Set password."""
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        """Check password."""
        return check_password_hash(self.password, value)

    def set_api_key(self):
        value = hexlify(os.urandom(256)).decode()
        self.api_key = value

    @property
    def full_name(self):
        """Full user name."""
        return "{0} {1}".format(self.first_name, self.last_name)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Object User {} , {}, {}, {}, {}, {}>'.format(self.id,
                                                       self.email,
                                                       self.phone_number,
                                                       self.first_name,
                                                       self.last_name,
                                                       self.password)

    def __str__(self):
        """Represent instance as a unique string."""
        return '<User {} , {}, {}, {}, {}, {}>'.format(str(self.id),
                                                       str(self.email),
                                                       str(self.phone_number),
                                                       str(self.first_name),
                                                       str(self.last_name),
                                                       str(self.password))

# if __name__ == '__main__':
#     print('main method called')


'''
-- Auto-generated SQL script #202003300908
SQL INSERTION
-- Auto-generated SQL script #202003301046
INSERT INTO public."user" (user_id,email,first_name,
last_name,phone_number,"password",creation_time,
modification_time)
VALUES (NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);

'''

'''
UserMixin supplies few helper method from flask_user
'''
