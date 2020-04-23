from extensions import db


class FcmTokens(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(200), nullable=False, unique=True)
    # person_id = db.Column(db.String(20), nullable=False)

    person_id = db.Column(db.Integer,
                          db.ForeignKey('user.id'),
                          nullable=False)
    db.UniqueConstraint('token', 'person_id',
                        'fcm_token_person_id'),

    def to_dict(self):
        return {
            'id': self.id,
            'token': self.token,
            'person_id': self.person_id,
        }

    def __init__(self, token=None,
                 person_id=None):
        self.token = token
        # person id is the current user id
        self.person_id = person_id

    def serialize(self):
        return {
                    'id': self.id,
                    'token': self.token,
                    'person_id': self.person_id,
                }
