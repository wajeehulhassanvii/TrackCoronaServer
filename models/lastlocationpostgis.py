from geoalchemy2 import Geometry
import datetime as dt
from extensions import db


class LastLocationPostGis(db.Model):
    """Simple database model to track the last location of an active user."""

    __tablename__ = 'last_location_post_gis'
    userId = db.Column(db.Integer, db.Sequence('user_id_seq'),
                       primary_key=True)
    latestPoint = db.Column(Geometry(geometry_type='POINT', srid=4326))
    lastModified = db.Column(db.TIMESTAMP(120))
    active = db.Column(db.BOOLEAN(120))

    def __init__(self, point=None, active=None):
        self.point = point
        self.lastModified = dt.datetime.utcnow
        self.active = active
