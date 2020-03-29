import os
from extensions import db
from extensions import bcrypt

from flask_login import UserMixin

import datetime as dt
from binascii import hexlify
from werkzeug import security


class User(UserMixin, db.Model):
    """Simple database model to track event attendees."""
    __name__ = 'User Table VARIABLE'
    __tablename__ = 'user'
    userId = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=False)
    creationTime = db.Column(db.DateTime, nullable=False,
                             default=dt.datetime.utcnow)
    last_name = db.Column(db.String(30), nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    phoneNumber = db.Column(db.String(80), nullable=False)

    ckeckVariable = 'My name is wajeeh CHECKING'

    def __init__(self,
                 userId=None,
                 email=None,
                 password=None,
                 phoneNumber=None,
                 firstName=None,
                 lastName=None,
                 ):
        self.email = email
        if password:
            self.password = security.generate_password_hash(password)
        else:
            self.password = None
        self.phoneNumber = phoneNumber
        self.first_name = firstName
        self.creationTime = dt.datetime.utcnow

    def set_password(self, password):
        """Set password."""
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        """Check password."""
        return bcrypt.check_password_hash(self.password, value)

    def set_api_key(self):
        value = hexlify(os.urandom(256)).decode()
        self.api_key = value

    @property
    def full_name(self):
        """Full user name."""
        return "{0} {1}".format(self.first_name, self.last_name)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<User %r>' % (self.checkVariable)

# if __name__ == '__main__':
#     print('main method called')
