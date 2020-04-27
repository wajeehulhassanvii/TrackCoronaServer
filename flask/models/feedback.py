from extensions import db
import datetime as dt


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    subject = db.Column(db.String(150), nullable=False)
    message = db.Column(db.String(1000), nullable=False)
    received_at = db.Column(db.TIMESTAMP(120), nullable=False,
                              default=dt.datetime.utcnow())
    # person_id = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'subject': self.subject,
            'message': self.message,
            'received_at': self.received_at,
        }

    def __init__(self, name=None,
                 email=None,
                 subject=None,
                 message=None):
        self.name = name
        self.email = email
        self.subject = subject
        self.message = message
        self.received_at = dt.datetime.utcnow()

    def serialize(self):
        return {
                    'id': self.id,
                    'name': self.name,
                    'email': self.email,
                    'subject': self.subject,
                    'message': self.message,
                    'received_at': self.received_at,
                }
