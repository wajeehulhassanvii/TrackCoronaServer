from geoalchemy2 import Geometry
import datetime as dt
from extensions import db

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class LastLocationPostGis(db.Model):
    """Simple database model to track the last location of an active user."""

    __tablename__ = 'last_location_post_gis'
    user_id = db.Column(db.Integer,
                        primary_key=True)
    latest_point = db.Column(Geometry(geometry_type='POINT',
                                      srid=4326),
                             nullable=True)
    last_modified = db.Column(db.TIMESTAMP(120), nullable=True,
                              default=dt.datetime.utcnow)
    active = db.Column(db.BOOLEAN(120), nullable=False)
#   define relationships with other tables
    person_id = db.Column(db.Integer,
                          db.ForeignKey('user.id'),
                          nullable=False)

    def __init__(self, point=None, active=None, person_id=None):
        self.point = point
        self.last_modified = dt.datetime.utcnow
        self.active = active
        self.person_id = person_id
