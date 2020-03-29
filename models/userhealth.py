from extensions import db


class UserHealth(db.Model):
    """Simple database model the health of the user"""
    __tablename__ = 'user_health'
    userId = db.Column(db.Integer, primary_key=True)
    personHealth = db.Column(db.String(80))

    def __init__(self, userId=None, userHealth=None):
        self.personHealth = userHealth
