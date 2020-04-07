
from extensions import app
from extensions import db
from extensions import session
from extensions import login_manager

from flask import jsonify, request
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import jwt_refresh_token_required
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_raw_jwt
from flask_jwt_extended import get_jwt_claims
from flask_jwt_extended import fresh_jwt_required

from exceptions import TokenNotFound

from blacklist_helpers import (
    is_token_blacklisted, add_token_to_blacklist
)

from sqlalchemy import func
from geoalchemy2 import WKBElement, WKTElement
from geoalchemy2.shape import from_shape
# from geoalchemy2 import WKBSpatialElement
from sqlalchemy import cast
from shapely.geometry.point import Point
from decimal import Decimal

from extensions import json
from flask_json import FlaskJSON, JsonError, json_response, as_json

# from geoalchemy2 import ST_DFullyWithin
# from geoalchemy2 import WKBElement
# from geoalchemy2 import WKSpatialElement
# from geoalchemy2.functions import functions
# from sqlalchemy import func

from models.userhealth import UserHealth
from models.user import User
from models.lastlocationpostgis import LastLocationPostGis
from flask_bcrypt import generate_password_hash


@app.route('/sendregistrationdata', methods=['POST', 'GET'])
def send_registration_data():
    if request.method == 'POST':
        data = request.get_json(force=True)

        try:
            email = data['email']
            first_name = data['firstName']
            last_name = data['lastName']
            phone_number = data['phoneNumber']
            # hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'),
            #                                 bcrypt.gensalt())
            password = data['password']
            hashed_password = generate_password_hash(password).decode('utf-8')
            email_exists = User.query.filter_by(email=email).first()
            phone_exists = User.query.filter_by(phone_number=phone_number).first()
            if email_exists is not None:
                return jsonify({"message": str("email\
                    associated with another account")}), 400
            if phone_exists is not None:
                return jsonify({"message": str("phone number\
                    associated with another account")}), 400
        except KeyError as err:
            print(err)
            return jsonify({"message": str("key error")}), 400
        new_user = User(email, hashed_password, phone_number, first_name,
                        last_name)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": str("Account successfully created")}), 200

    if request.method == 'GET':
        print('inside get method')
        return jsonify({"message": str("GET sendregistrationdata\
        function working")}), 200


@app.route('/login', methods=['GET', 'POST'])
def loginUser():
    if request.method == 'POST':
        request_data = request.get_json(force=True)
        try:
            email = str(request_data['email'])
            user = User.query.filter_by(email=email).first()
            # remember_me = request_data['rememberMe']
            print('email {}'.format(email))
            print(str(user))
            if user is not None:
                password = request_data['password']
                if user.check_password(password):
                    access_token = create_access_token(identity=user.id, fresh=True)
                    refresh_token = create_refresh_token(user.id)
                    return jsonify({
                        "message": str("login\
                        successful"),
                        "access_token": access_token,
                        "refresh_token": refresh_token
                                    }), 200
                else:
                    return jsonify({"message": str("password\
                     incorrect")}), 400
            else:
                return jsonify({"message": str("email\
                     does not have any associated account")}), 400
        except KeyError as err:
            print(err)
            return jsonify({"message": str("Key Error\
                during login")}), 400
        return jsonify({"message": str("Post Login Completed")}), 200

    if request.method == 'GET':
        print('inside get method')
        return jsonify({"message": str("GET login\
        function working")}), 200


# Standard refresh endpoint. A blacklisted refresh token
# will not be able to access this endpoint
@app.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    print('token refreshed')
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    ret = {
        'access_token': access_token
    }
    return jsonify(ret), 201


# def check_if_token_in_blacklist(decrypted_token):
#     jti = decrypted_token['jti']
#     return models.RevokedTokenModel.is_jti_blacklisted(jti)


# check token
@app.route('/checktoken', methods=['GET'])
@jwt_required
def get_tokens():
    user_identity = get_jwt_identity()
    all_tokens = get_user_tokens(user_identity)
    ret = [token.to_dict() for token in all_tokens]
    return jsonify(ret), 200


@app.route('/logout', methods=['DELETE'])
@jwt_required
def logout(token_id):
    ''' must provide access_token and refresh_token to logout the user
    upon logining in again, new access_token and refresh_token
    will be issued'''

    print('clearing user login from sessions')

    # Get and verify the desired revoked status from the body
    json_data = request.get_json(force=True)
    access_token = json_data['access_token']
    refresh_token = json_data['refresh_token']
    # Store the tokens in our store with a status of not currently revoked.
    add_token_to_blacklist(access_token, app.config['JWT_IDENTITY_CLAIM'])
    add_token_to_blacklist(refresh_token, app.config['JWT_IDENTITY_CLAIM'])

    return jsonify({"message": str("you are logged\
        out\nstay home stay safe!!!")}), 401


@app.route('/getuserswithindiameter', methods=['POST', 'GET'])
# @jwt_required
def get_users_within_diameter():
    '''
    get the geocoordinates of all the people in close proximity
    error-> 302: redirect when no login, otherwise success : 200
    '''
    print('before post method')
    if request.method == 'POST':
        request_data = request.get_json(force=True)
        print('inside post')
        try:
            main_user_latitude = request_data["userLatitude"]
            main_user_longitude = request_data["userLongitude"]
            main_user_condition = request_data["personCondition"]
            current_user_id = 1

            # Also check if active

            temp_lat = Decimal(main_user_latitude)
            temp_lon = Decimal(main_user_longitude)
            kms = 1
            approximate_degree_distance = kilometersToDegrees(kms)
            point = Point(temp_lon, temp_lat)
            point_wkt = WKTElement('SRID=4326;POINT({} {})'.format(temp_lon, temp_lat), srid=4326)
            print(point)
            # print(point_string)
            # update UserHealth with users health
            user_health_instance = db.session.query(UserHealth).filter(UserHealth.person_id == current_user_id).first()
            if(user_health_instance):
                user_health_instance.user_health = main_user_condition
                db.session.add(user_health_instance)
                db.session.commit()
            else:
                db.session.add(UserHealth(main_user_condition, current_user_id))
                db.session.commit()

            # update LastLocationGis with users last location
            last_loc_instance = db.session.query(LastLocationPostGis).filter(LastLocationPostGis.person_id == current_user_id).first()
            if(last_loc_instance):
                print('instance found')
                last_loc_instance.latest_point = point_wkt
                db.session.add(last_loc_instance)
                db.session.commit()
            else:
                print('instance not found')
                db.session.add(LastLocationPostGis(point_wkt, current_user_id))
                db.session.commit()
            # working

            # Find all points and remove our own point
            # wkb_element = from_shape(point)
            print(point_wkt)
            # wkb_point = WKBSpatialElement(buffer(point.wkb ), 4326 )
            list_of_users_filter = func.ST_DWithin(
                LastLocationPostGis.latest_point, point_wkt,
                1000)
            list_of_users = db.session.query(LastLocationPostGis).filter(list_of_users_filter).all()

            if len(list_of_users) > 0:
                print('list of users is more than 1')
                return jsonify(message=str("in side post"),
                               list_of_users=[e.serialize() for e in list_of_users]), 200
            else:
                return jsonify(message=str("in side post"),
                               list_of_users=[]), 200
        except KeyError as err:
            print(err)
            print('returning key error')
            return jsonify({"message": str(err)}), 200

    return jsonify({"message": str("function ends")}), 401


@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    return jsonify({'hello': 'world'})


def kilometersToDegrees(kilometers):
    return kilometers / 111.325


'''
BCRYPT USAGE

>>> import bcrypt
>>> password = b"super secret password"
>>> # Hash a password for the first time, with a randomly-generated salt
>>> hashed = bcrypt.hashpw(password, bcrypt.gensalt())
>>> # Check that a unhashed password matches one that has previously been
>>> #   hashed
>>> if bcrypt.hashpw(password, hashed) == hashed:
...     print("It Matches!")
... else:
...     print("It Does not Match :(")

'''

'''
POSTGRE SQL DB USAGE

>>> db.session.add(me)
>>> db.session.commit()
'''

'''
ENCODED BEFORE HASHING
str('asd').encode('utf-8')
'''

'''
to connect flask_login to user we use user_loader
'''


'''
eg 1
updating in sqlalchemy
user.no_of_logins += 1
session.commit()

eg2
session.query().\
        filter(User.username == form.username.data).\
        update({"no_of_logins": (User.no_of_logins +1)})
    session.commit()

eg3
_______
INSERT one
newToner = Toner(toner_id = 1,
                    toner_color = 'blue',
                    toner_hex = '#0F85FF')
dbsession.add(newToner)
dbsession.flush()

eg4

# db.session.query(LastLocationPostGis).filter(LastLocationPostGis.user_id == current_user_id).update({'latest_point': point})
_______
INSERT multiple
newToner1 = Toner(toner_id = 1,
                    toner_color = 'blue',
                    toner_hex = '#0F85FF')
newToner2 = Toner(toner_id = 2,
                    toner_color = 'red',
                    toner_hex = '#F01731')

dbsession.add_all([newToner1, newToner2])
dbsession.flush()
___________
UPDATE
q = dbsession.query(Toner)
q = q.filter(Toner.toner_id==1)
record = q.one()
record.toner_color = 'Azure Radiance'

dbsession.flush()

or using a fancy one-liner using MERGE

record = dbsession.merge(Toner( **kwargs))
--------------------------------------
ANOTHER EXAMPLE
b = create_engine('sqlite:////temp/test123.db')
metadata.create_all(db)

sm = orm.sessionmaker(bind=db, autoflush=True, autocommit=True, expire_on_commit=True)
session = orm.scoped_session(sm)

#create new Product record:
if session.query(Product).filter(Product.id==1).count()==0:
    new_prod = Product("1","Product1")
    print "Creating new product: %r" % new_prod
    session.add(new_prod)
    session.flush()
else:
    print "product with id 1 already exists: %r" % session.query(Product).filter(Product.id==1).one()

print "loading Product with id=1"
prod = session.query(Product).filter(Product.id==1).one()
print "current name: %s" % prod.name
prod.name = "new name"

print prod


prod.name = 'test'

session.add(prod)
session.flush()

print prod
------------------------------------------

class geoalchemy2.elements.WKTElement

Usage examples:

wkt_element_1 = WKTElement('POINT(5 45)')
wkt_element_2 = WKTElement('POINT(5 45)', srid=4326)
wkt_element_3 = WKTElement('SRID=4326;POINT(5 45)', extended=True)

https://stackoverflow.com/questions/23981056/geoalchemy-st-dwithin-implementation
'''
