# from ..app import db
from app import db
from geoalchemy2 import Geometry, Geography
from sqlalchemy import Column, Integer, String, Sequence, TIMESTAMP, BOOLEAN

class LastLocationPostGis(db.Model):
    """Simple database model to track the last location of an active user."""

    __tablename__ = 'last_location_post_gis'
    userId = db.Column(db.Integer, db.Sequence('user_id_seq'), primary_key=True)
    latestPoint = db.Column(Geography(geometry_type='POINT', srid=4326, spatial_index=False))
    lastModified = db.Column(db.TIMESTAMP(120))
    active = db.Column(db.BOOLEAN(120))

    def __init__(self, point=None, active=None):
        self.point = point
        self.lastModified = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
        self.active = active
