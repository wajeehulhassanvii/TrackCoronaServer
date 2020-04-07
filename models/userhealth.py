from extensions import db


class UserHealth(db.Model):
    """Simple database model the health of the user"""
    __tablename__ = 'user_health'
    user_id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_health = db.Column(db.String(80), nullable=False)
#   Define relation with other tables
    person_id = db.Column(db.Integer,
                          db.ForeignKey('user.id'),
                          nullable=False)

    def __init__(self,
                 user_health=None,
                 person_id=None):
        self.user_id = person_id
        self.user_health = user_health
        self.person_id = person_id
