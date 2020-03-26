from ..app import db


class personHealth(db.Model):
    """Simple database model to track event attendees."""

    __tablename__ = 'personHealth'
    userId = db.Column(db.Integer, primary_key=True)
    personHealth = db.Column(db.String(80))

    def __init__(self, name=None, personHealth=None):
        self.personHealth = personHealth
