from datetime import datetime

from sqlalchemy.orm.exc import NoResultFound
from flask_jwt_extended import decode_token


from models.token_blacklist import TokenBlacklist
from extensions import db
from extensions import jwt


def _epoch_utc_to_datetime(epoch_utc):
    """
    Helper function for converting epoch timestamps (as stored in JWTs) into
    python datetime objects (which are easier to use with sqlalchemy).
    """
    return datetime.fromtimestamp(epoch_utc)


def add_token_to_blacklist(encoded_token, identity_claim):
    """
    Adds a new token to the database. It is not revoked when it is added.
    :param identity_claim:
    """
    decoded_token = decode_token(encoded_token)
    jti = decoded_token['jti']
    user_identity = decoded_token[identity_claim]

    db_token = TokenBlacklist(
        jti=jti,
        user_identity=user_identity
    )
    db.session.add(db_token)
    db.session.commit()


@jwt.token_in_blacklist_loader
def is_token_blacklisted(decoded_token):
    """
    Checks if the given token is revoked or not. Because we are adding all the
    tokens that we create into this database, if the token is not present
    in the database we are going to consider it revoked, as we don't know where
    it was created.
    """
    jti = decoded_token['jti']
    try:
        token = TokenBlacklist.query.filter_by(jti=jti).one()
        if token:
            return True
        else:
            return False
    except NoResultFound:
        return False
