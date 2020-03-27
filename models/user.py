# import os
from app import db
from app import UserMixin

import datetime as dt
from binascii import hexlify
# from flask_login import UserMixin
from werkzeug import security

class User(UserMixin, db.Model):
    """Simple database model to track event attendees."""

    __tablename__ = 'user'
    userId = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    last_name = db.Column(db.String(30), nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    phoneNumber = db.Column(db.String(80), nullable=False)

    def __init__(self, userId=None,
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
        self.first_name = first_name

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
        return "<User({email!r})>".format(email=self.email)
