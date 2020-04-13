from datetime import datetime

from sqlalchemy.orm.exc import NoResultFound
from flask_jwt_extended import decode_token


from models.token_blacklist import TokenBlacklist
from extensions import db
from extensions import jwt
from exceptions import TokenNotFound


def _epoch_utc_to_datetime(epoch_utc):
    """
    Helper function for converting epoch timestamps (as stored in JWTs) into
    python datetime objects (which are easier to use with sqlalchemy).
    """
    return datetime.fromtimestamp(epoch_utc)


def add_token_to_blacklist(encoded_token, identity_claim, is_revoked):
    """
    Adds a new token to the database. It is not revoked when it is added.
    :param identity_claim:
    """
    decoded_token = decode_token(encoded_token)
    jti = decoded_token['jti']
    token_type = decoded_token['type']
    user_identity = str(decoded_token[identity_claim]['id'])
    expires = _epoch_utc_to_datetime(decoded_token['exp'])
    revoked = is_revoked

    db_token = TokenBlacklist(
        jti=jti,
        token_type=token_type,
        user_identity=user_identity,
        revoked=revoked,
        expires=expires,
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
    print(' checking if token is in the blacklist or not')
    jti = decoded_token['jti']
    token = TokenBlacklist.query.filter_by(jti=jti).first()
    if (token is not None):
        print(type(token))
        return token.revoked
    else:
        print(' no token in the database, please login in again')
        return True


def get_user_tokens(user_identity):
    """
    Returns all of the tokens, revoked and unrevoked, that are stored for the
    given user
    """
    return TokenBlacklist.query.filter_by(user_identity=user_identity).all()
