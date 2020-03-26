from ..app import db


class LastLocationPostGis(db.Model):
    """Simple database model to track event attendees."""

    __tablename__ = 'guests'
    userId = db.Column(db.Integer, primary_key=True)
    latestPoint = db.Column(db.point(80))
    lastModified = db.Column(db.TIMESTAMPTZ(120))
    active = db.Column(db.boolean(120))

    def __init__(self, point=None, lastModified=None, active=None):
        self.point = point
        self.lastModified = lastModified
        self.active = active
