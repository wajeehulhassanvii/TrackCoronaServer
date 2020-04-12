from extensions import db
import datetime as dt
from geoalchemy2.shape import to_shape
from geoalchemy2 import Geography


class InteractedUsers(db.Model):
    __tablename__ = 'interacted_users'
    interacted_id = db.Column(db.Integer,
                              primary_key=True)
    at_location = db.Column(Geography(geometry_type='POINT',
                                      srid=4326),
                            nullable=True)
    at_time = db.Column(db.TIMESTAMP(120), nullable=True,
                        default=dt.datetime.utcnow())

#   define relationships with other tables
    person_id = db.Column(db.Integer,
                          db.ForeignKey('user.id'),
                          nullable=False)
    db.UniqueConstraint('interacted_id', 'person_id',
                        'person_interaction'),

    def __init__(self, point=None,
                 person_id=None,
                 interacted_id=None):
        self.at_location = point
        # default
        self.at_time = dt.datetime.utcnow()
        # person id is the current user id
        self.person_id = person_id
        # we will get this from post api call
        self.interacted_id = interacted_id

    def serialize(self):
        return {
                    'interacted_id': self.interacted_id,
                    'at_location_lat': str(to_shape(self.at_location).y),
                    'at_location_lon': str(to_shape(self.at_location).x),
                    'at_time': self.at_time,
                    'person_id': self.person_id,
                }
