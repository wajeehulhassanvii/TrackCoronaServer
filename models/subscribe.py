from extensions import db


class Subscribe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
        }

    def __init__(self,
                 email=None):
        self.email = email

    def serialize(self):
        return {
                    'id': self.id,
                    'email': self.email,
                }
