
from extensions import app
from app import db
from extensions import session
from extensions import login_manager
from app import jwt

from flask import jsonify, request
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import jwt_refresh_token_required
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_raw_jwt
from flask_jwt_extended import get_jwt_claims
from flask_jwt_extended import fresh_jwt_required
from flask_jwt_extended import get_jti

from exceptions import TokenNotFound

from blacklist_helpers import (
    is_token_blacklisted, add_token_to_blacklist
)


import datetime as dt
import json
from sqlalchemy.sql import table, column
from sqlalchemy import func
from geoalchemy2 import WKTElement
from geoalchemy2.shape import from_shape, to_shape
# from geoalchemy2 import WKBSpatialElement
from shapely.geometry.point import Point
from decimal import Decimal

from flask_json import FlaskJSON, JsonError, json_response, as_json

from blacklist_helpers import get_user_tokens

# from geoalchemy2 import ST_DFullyWithin
# from geoalchemy2 import WKBElement
# from geoalchemy2 import WKSpatialElement

from models.userhealth import UserHealth
from models.user import User
from models.lastlocationpostgis import LastLocationPostGis
from models.userlocationandhealth import UserLocationAndHealth
from models.interactedusers import InteractedUsers
from models.token_blacklist import TokenBlacklist
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
        new_user = User(email, hashed_password, phone_number,
                        first_name,
                        last_name)        
        db.session.add(new_user)
        db.session.commit()
        temp_new_user_serialized = new_user.serialize()
        access_token = create_access_token(identity=new_user)
        refresh_token = create_refresh_token(identity=new_user)

        return jsonify({"message": str("Account successfully\
             created"),
                        "access_token": access_token,
                        "refresh_token": refresh_token}), 200

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
                    print('putting user as identity {}'.format(user))
                    access_token = create_access_token(identity=user,
                                                       fresh=True)
                    refresh_token = create_refresh_token(user)
                    add_token_to_blacklist(access_token, app.config['JWT_IDENTITY_CLAIM'], False)
                    add_token_to_blacklist(refresh_token, app.config['JWT_IDENTITY_CLAIM'], False)
                    return jsonify({
                        "message": str("login successful"),
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


@jwt.user_identity_loader
def user_identity_lookup(user):
    print('user in the user_identity_lookup: {}'.format(user))
    print(type(user))
    if(type(user) == dict):
        print(type(user))
        temp_user = User.query.filter_by(email=str(user['email'])).first()
        temp_user_serialized = temp_user.serialize()
    else:
        temp_user = User.query.filter_by(email=user.email).first()
        temp_user_serialized = temp_user.serialize()
    # return User.query.filter_by(email=user.email).first().email
    print('----------------loading identity-----------')
    return temp_user_serialized


# Standard refresh endpoint. A blacklisted refresh token
# will not be able to access this endpoint
''' Endpoints decorated with @jwt_refresh_token_required
require that an Authorization: Bearer {refresh_token}
header is included in the request.'''


@app.route('/fresh-login', methods=['POST'])
def fresh_login():
    request_data = request.get_json(force=True)
    email = str(request_data['email'])
    password = request_data['password']
    user = User.query.filter_by(email=email).first()
    if user.check_password(password):
        access_token = create_access_token(identity=user,
                                           fresh=True)
        return jsonify({
            "access_token": access_token
                        }), 200
    else:
        return jsonify({
            "access_token": access_token
                        }), 200


@app.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    print('inside token refreshed method')
    current_user = get_jwt_identity()
    print('------current user------- {}'.format(current_user))
    access_token = create_access_token(identity=current_user, fresh=False)
    print(access_token)
    add_token_to_blacklist(access_token, app.config['JWT_IDENTITY_CLAIM'], False)
    return jsonify({"access_token": access_token}), 200


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
def logout():
    jti = get_raw_jwt()['jti']
    # Store the tokens in our store with a status of not currently revoked.
    token_temp = db.session.query(TokenBlacklist).filter_by(jti=jti).first()
    token_temp.revoked = True
    db.session.add(token_temp)
    db.session.commit()
    print('token pushed to database')
    return jsonify({"message": str("you are logged\
        out\nstay home stay safe!!!")}), 200


@app.route('/logoutrefresh', methods=['DELETE'])
@jwt_refresh_token_required
def logout_refresh():
    # jti = get_raw_jwt()['jti']
    
    request_data = request.get_json(force=True)
    refresh_token = str(request_data['refresh_token'])
    refresh_token_jti = get_jti(refresh_token)
    
    # token_type = decoded_token['type']
    # Store the tokens in our store with a status of not currently revoked.
    token_temp = db.session.query(TokenBlacklist).filter_by(jti=refresh_token_jti).first()
    token_temp.revoked = True
    db.session.add(token_temp)
    db.session.commit()
    print('revoked the refresh token')
    return jsonify({"message": str("you are logged\
        out\nstay home stay safe!!!")}), 200


@app.route('/deleteuser', methods=['DELETE'])
@fresh_jwt_required
def delete_the_user():
    # jti = get_raw_jwt()['jti']
    request_data = request.get_json(force=True)
    refresh_token = str(request_data['refresh_token'])
    refresh_token_jti = get_jti(refresh_token)
    access_token = str(request_data['access_token'])
    access_token_jti = get_jti(access_token)
    refresh_identity = get_jwt_identity()
    person_id = refresh_identity['id']
    print(person_id, type(person_id))
    # token_type = decoded_token['type']
    # Store the tokens in our store with a status of not currently revoked.
    db.session.query(TokenBlacklist).filter_by(jti=refresh_token_jti).delete()
    db.session.query(TokenBlacklist).filter_by(jti=access_token_jti).delete()
    db.session.query(UserHealth).filter_by(person_id=person_id).delete()
    db.session.query(LastLocationPostGis).filter_by(person_id=person_id).delete()
    db.session.query(InteractedUsers).filter_by(interacted_id=person_id).delete()
    db.session.query(InteractedUsers).filter_by(person_id=person_id).delete()
    db.session.query(User).filter_by(id=person_id).delete()
    db.session.query(TokenBlacklist).filter_by(user_identity=str(person_id)).delete()
    db.session.commit()
    print('deleted the user')
    return jsonify({"message": str("your account\
        has been deleted\nstay safe keep your family safe!!!")}), 200


@app.route('/getuserswithindiameter', methods=['POST', 'GET'])
@jwt_required
def get_users_within_diameter():
    '''
    make sure person condition and location both are present
    otherwise return error
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
            temp_identity = get_jwt_identity()
            current_user_id = temp_identity['id']
            print('{}   {}'.format(current_user_id, type(current_user_id)))

            # Also check if active

            temp_lat = Decimal(main_user_latitude)
            temp_lon = Decimal(main_user_longitude)

            point_wkt = WKTElement('SRID=4326;POINT({} {})'.format(temp_lon, temp_lat), srid=4326)
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
                last_loc_instance.last_modified = dt.datetime.utcnow()
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
            list_of_users = db.session.query(LastLocationPostGis).filter(LastLocationPostGis.active==True).filter(list_of_users_filter).order_by(LastLocationPostGis.person_id).all()

            if len(list_of_users) > 0:

                temp_list_user_ids = []
                for every_user in list_of_users:
                    temp_list_user_ids.append(every_user.person_id)

                temp_list_users_conditions = db.session.query(UserHealth).filter(UserHealth.person_id.in_(temp_list_user_ids)).order_by(UserHealth.person_id).all()
                print('')
                list_of_user_location_and_health = []
                for i in range(len(list_of_users)):
                    temp_obj = UserLocationAndHealth(str(to_shape(list_of_users[i].latest_point).y),
                                                     str(to_shape(list_of_users[i].latest_point).x),
                                                     list_of_users[i].person_id,
                                                     temp_list_users_conditions[i].user_health)
                    list_of_user_location_and_health.append(temp_obj)

                user_location_health_return = [e.serialize() for e in list_of_user_location_and_health]
                return jsonify(
                    message=str("fetching complete ....."),
                    list_of_user_location_and_health=(user_location_health_return),), 200
            else:
                return jsonify(message=str("in side post"),
                               list_of_users=[]), 200
        except KeyError as err:
            print(err)
            print('returning key error')
            return jsonify({"message": str(err)}), 200

    return jsonify({"message": str("function ends")}), 401


@app.route('/getappuserstats', methods=['POST', 'GET'])
# @jwt_required
def get_app_user_stats():
    if request.method == 'GET':
        print('inside get')
        app_user_stats = db.session.query(UserHealth.user_health, func.count(UserHealth.user_health)).group_by(UserHealth.user_health).all()
        print(app_user_stats)
    return jsonify({"message": 'stats fetched',
                    "total_user_stats": app_user_stats}), 200


@app.route('/deleteuserhealthandlocation', methods=['DELETE', 'GET'])
@jwt_required
def delete_user_health_and_location():
    print(request)
    if request.method == 'DELETE':
        # try:
        main_person_id = get_jwt_identity()['id']
        print('userid recieved: {}'.format(main_person_id))
        main_person_id = Decimal(main_person_id)

        main_user_location_record = db.session.query(LastLocationPostGis).filter(LastLocationPostGis.person_id == main_person_id)
        if main_user_location_record:
            print('data exists for deletion')
            db.session.query(LastLocationPostGis).filter(LastLocationPostGis.person_id==main_person_id).delete()
            db.session.commit()

            main_user_health_record = db.session.query(UserHealth).filter(UserHealth.person_id == main_person_id)
            if main_user_health_record:
                print('data exists for deletion.')
                db.session.query(UserHealth).filter(UserHealth.person_id == main_person_id).delete()
                db.session.commit()
            else:
                return jsonify(message=str("no health or location record found")), 200

    return jsonify(message=str("in side post")), 200


@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    return jsonify({'hello': 'world'})


@app.route('/interactedusers', methods=['POST', 'GET'])
@jwt_required
def interactedusers():
    # TODO update the interactedTable and add another id,
    # making interacted_id and person_id the
    if request.method == 'POST':
        print('inside post of interactedusers')
        request_data = request.get_json(force=True)
        main_person_id = get_jwt_identity()['id']
        # user_email = get_jwt_identity()['email']
        # this statement is not needed
        # print('this is user: {}'.format(User.query.filter_by(email=user_email).first()))
        # main_person_id = db.session.query(User.id).filter(User.email == user_email).first()

        # also if the interaction is already present then update the interaction
        for n in range(len(request_data['listOfInteractedUsers'])):
            print(request_data['listOfInteractedUsers'][n]['lat'])
            temp_lat = Decimal(request_data['listOfInteractedUsers'][n]['lat'])
            temp_lon = Decimal(request_data['listOfInteractedUsers'][n]['lng'])
            temp_interacted_id = Decimal(request_data['listOfInteractedUsers'][n]['interacted_id'])
            temp_user = db.session.query(InteractedUsers).filter(InteractedUsers.person_id==main_person_id).filter(InteractedUsers.interacted_id==temp_interacted_id).first()
            if temp_user:
                print('this is in interaction, update the location and timestamp')
                point_wkt = WKTElement('SRID=4326;POINT({} {})'.format(temp_lon, temp_lat), srid=4326)
                temp_user.at_location = point_wkt
                temp_user.at_time = dt.datetime.utcnow()
                db.session.add(temp_user)
            else:
                print('not present so entering into db')
                point_wkt = WKTElement('SRID=4326;POINT({} {})'.format(temp_lon, temp_lat), srid=4326)
                db.session.add(InteractedUsers(point_wkt, main_person_id, temp_interacted_id))
        db.session.commit()
        print('pushed all the interacted user points to the database')
        # db.session.add(InteractedUsers())
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

print(type(list_of_users[0].latest_point))
print(type(str(to_shape(list_of_users[0].latest_point))))
print(func.ST_Transform(list_of_users[0].latest_point, 4326))
return jsonify(message=str("in side post"),


https://stackoverflow.com/questions/23981056/geoalchemy-st-dwithin-implementation
'''
