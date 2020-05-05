
from extensions import app
from app import db
from extensions import session
from extensions import login_manager
from extensions import mail
from flask_mail import Message
from app import jwt

from flask import jsonify, request, render_template
import flask
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import jwt_refresh_token_required
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_raw_jwt
from flask_jwt_extended import get_jwt_claims
from flask_jwt_extended import fresh_jwt_required
from flask_jwt_extended import get_jti, jwt_optional
from flask_jwt_extended import decode_token

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
from models.fcm_tokens import FcmTokens
from models.user import User
from models.lastlocationpostgis import LastLocationPostGis
from models.userlocationandhealth import UserLocationAndHealth
from models.interactedusers import InteractedUsers
from models.token_blacklist import TokenBlacklist
from models.feedback import Feedback
from models.subscribe import Subscribe
from flask_bcrypt import generate_password_hash

from extensions import push_service
from flask_cors import CORS


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
# @jwt_refresh
def loginUser():
    if request.method == 'POST':
        # TODO change this to jwt_refresh
        # TODO check existing access and refresh token first,
        # TODO if present then turn revoke to false
        # TODO else create new if password correct
        # TODO delete older token than time defined
        # TODO if authorization is not present then create both token, 200
        # TODO if authorization is present then don't create both tokens, 205
        # TODO check existing access and refresh token first,
        # TODO if present then turn revoke to false
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
                    token_type = str(request_data['token_type'])
                    old_refresh_token_encoded = ""
                    if token_type == "refresh":
                        print('token type is refresh do from here')
                        # TODO check if refresh is revoked
                        old_refresh_token_encoded = request_data['old_refresh_token']
                        old_refresh_jti_decoded = decode_token(old_refresh_token_encoded)['jti']
                        print(old_refresh_jti_decoded)
                        # TODO change revoked to false and create new access
                        token_temp = db.session.query(TokenBlacklist).filter_by(jti=old_refresh_jti_decoded).first()
                        token_temp.revoked = False
                        print('step1')
                        # TODO old access token change revoke
                        # TODO check if refresh is revoked
                        print('step2')
                        old_access_token_encoded = request_data['old_access_token']
                        print('step3')
                        old_access_jti_decoded = decode_token(old_access_token_encoded, allow_expired=True)['jti']
                        print('step4')
                        print(old_access_jti_decoded)
                        # TODO change revoked to false and create new access
                        print('step5')
                        token__access_temp = db.session.query(TokenBlacklist).filter_by(jti=old_access_jti_decoded).first()
                        print('step6')
                        token__access_temp.revoked = False
                        # TODO old access token change revoke
                        db.session.commit()
                    else:
                        refresh_token = create_refresh_token(user)
                        add_token_to_blacklist(refresh_token, app.config['JWT_IDENTITY_CLAIM'], False)
                        old_refresh_token_encoded = refresh_token
                    print(token_type)
                    print('putting user as identity {}'.format(user))
                    access_token = create_access_token(identity=user,
                                                       fresh=True)
                    add_token_to_blacklist(access_token, app.config['JWT_IDENTITY_CLAIM'], False)
                    return jsonify({
                        "message": str("login successful"),
                        "access_token": access_token,
                        "refresh_token": old_refresh_token_encoded
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


@app.route('/checklogin', methods=['GET'])
@jwt_optional
def check_login():
    if request.method == 'GET':
        print('break after 1')
        jwt_user = get_jwt_identity()
        if jwt_user:
            print('break after 2')
            jwt_user = jwt_user['id']
            print('break after 3')
            is_jwt_revoked = db.session.query(TokenBlacklist.revoked).filter(TokenBlacklist.user_identity==str(jwt_user)).first()
            print('break after 4')
            print('is jwt revoked {}'.format(is_jwt_revoked))
            return jsonify({"message": str("GET login\
                function working"),
                "is_jwt_revoked": is_jwt_revoked[0]}), 200
        else:
            return jsonify({"message": str("GET login\
                function working"),
                "is_jwt_revoked": False}), 400
        return jsonify({"message": str("check login\
    function working")}), 400
    return jsonify({"message": str("check login\
    function working")}), 400


@jwt.user_identity_loader
def user_identity_lookup(user):
    print('user in the user_identity_lookup: {}'.format(user))
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


@app.route('/freshlogin', methods=['POST'])
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
    # TODO check database if token is revoked then
    # TODO authenticate the expired token
    # TODO don't issue if
    # TODO also check if refresh is revoked, if revoked don't issue
    # TODO otherwise issue
    # don't issue if
    current_user = get_jwt_identity()
    print('------current user------- {}'.format(current_user))
    # TODO retrieve access_token from JSON body and see if token is present in DB
    access_token = create_access_token(identity=current_user, fresh=False)
    print('new access_token: {}'.format(access_token))
    # person_id = current_user['id']
    # TODO delete expired tokens after matching them in DB
    request_data = request.get_json(force=True)
    old_access_token_encoded = request_data['access_token']
    if old_access_token_encoded:
        decoded_access_token = decode_token(old_access_token_encoded, allow_expired=True)
        old_access_jti = decoded_access_token['jti']
        if db.session.query(TokenBlacklist).filter_by(jti=old_access_jti).first():
            print('old access token is present')
            db.session.query(TokenBlacklist).filter_by(jti=old_access_jti).delete()
            db.session.commit()
    add_token_to_blacklist(access_token, app.config['JWT_IDENTITY_CLAIM'], False)
    print('new current user n access_token pushed to db')
    return jsonify({"access_token": access_token}), 200


@app.route('/logout', methods=['DELETE'])
@jwt_required
def logout():
    jti = get_raw_jwt()['jti']
    # Store the tokens in our store with a status of not currently revoked.
    token_temp = db.session.query(TokenBlacklist).filter_by(jti=jti).first()
    token_temp.revoked = True
    db.session.add(token_temp)
    db.session.commit()
    print('token pushed to database for delete')
    return jsonify({"message": str("you are logged\
        out\nstay home stay safe!!!")}), 200


@app.route('/logoutrefresh', methods=['DELETE'])
@jwt_refresh_token_required
def logout_refresh():
    # jti = get_raw_jwt()['jti']
    if request.method == 'DELETE':
        request_data = request.get_json(force=True)
        print('here1')
        refresh_token = str(request_data['refresh_token'])
        print('here2')
        refresh_token_jti = get_jti(refresh_token)
        # token_type = decoded_token['type']
        # Store the tokens in our store with a status of not currently revoked.
        token_temp = db.session.query(TokenBlacklist).filter_by(jti=refresh_token_jti).first()
        print('here3')
        token_temp.revoked = True
        print('here4')
        db.session.add(token_temp)
        print('here5')
        db.session.commit()
        print('revoked the refresh token')
        return jsonify({"message": str("you are logged\
            out\nstay home stay safe!!!")}), 200
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
            # print('{}   {}'.format(current_user_id, type(current_user_id)))

            # Also check if active

            temp_lat = Decimal(main_user_latitude)
            temp_lon = Decimal(main_user_longitude)

            point_wkt = WKTElement('SRID=4326;POINT({} {})'.format(temp_lon, temp_lat), srid=4326)
            # print(point_string)
            # update UserHealth with users health
            user_health_instance = db.session.query(UserHealth).filter(UserHealth.person_id == current_user_id).first()
            if(user_health_instance):
                # TODO implement this with celery
                user_health_instance.user_health = main_user_condition
                db.session.add(user_health_instance)
                db.session.commit()
            else:
                # TODO implement this with celery
                db.session.add(UserHealth(main_user_condition, current_user_id))
                db.session.commit()

            # update LastLocationGis with users last location
            last_loc_instance = db.session.query(LastLocationPostGis).filter(LastLocationPostGis.person_id == current_user_id).first()
            if(last_loc_instance):
                print('instance found')
                # TODO implement this with celery
                last_loc_instance.latest_point = point_wkt
                last_loc_instance.last_modified = dt.datetime.utcnow()
                db.session.add(last_loc_instance)
                db.session.commit()
            else:
                # TODO implement this with celery
                print('instance not found')
                db.session.add(LastLocationPostGis(point_wkt, current_user_id))
                db.session.commit()
            # working

            # Find all points and remove our own point
            # wkb_element = from_shape(point)
            # print(point_wkt)
            # wkb_point = WKBSpatialElement(buffer(point.wkb ), 4326 )
            list_of_users_filter = func.ST_DWithin(
                LastLocationPostGis.latest_point, point_wkt,
                1000)
            
            list_of_users = db.session.query(LastLocationPostGis).filter(LastLocationPostGis.active==True).filter(list_of_users_filter).order_by(LastLocationPostGis.person_id).all()

            if len(list_of_users) > 0:

                temp_list_user_ids = []
                # TODO paralellize for loop
                for every_user in list_of_users:
                    temp_list_user_ids.append(every_user.person_id)

                temp_list_users_conditions = db.session.query(UserHealth).filter(UserHealth.person_id.in_(temp_list_user_ids)).order_by(UserHealth.person_id).all()
                list_of_user_location_and_health = []
                # TODO paralellize for loop
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


@app.route('/getappuserstats', methods=['GET'])
@jwt_required
def get_app_user_stats():
    if request.method == 'GET':
        print('inside get')
        app_user_stats = db.session.query(UserHealth.user_health, func.count(UserHealth.user_health)).group_by(UserHealth.user_health).all()
        print(app_user_stats)
    return jsonify({"message": 'stats fetched',
                    "total_user_stats": app_user_stats}), 200


@app.route('/savefcmtoken', methods=['POST', 'GET'])
@jwt_optional
def save_fcm_token():
    if request.method == 'POST':
        print('inside savefcmtoken POST')
        request_data = request.get_json()
        fcb_token = request_data['fcm_token']
        old_fcb_token = request_data['old_fcm_token']
        main_person_id = get_jwt_identity()
        if main_person_id:
            main_person_id = main_person_id['id']
        else:
            print('don\'t save without token')
            return jsonify({"message": 'savefcmtoken: id for fcm_token\
 not in jwt but initialized in app'}), 200
        if db.session.query(FcmTokens).filter(FcmTokens.token == fcb_token).first():
            print('same token present, don\'t save')
            return jsonify({"message": 'savefcmtoken: fcm token already present for user'}), 200
        else:
            print('fcb token not present, save')
            db.session.query(FcmTokens).filter(FcmTokens.token == old_fcb_token).delete()
            new_token = FcmTokens(fcb_token, str(main_person_id))
            db.session.add(new_token)
            db.session.commit()
    return jsonify({"message": 'savefcmtoken: fcm token stored'}), 200


@app.route('/deletefcmtoken', methods=['POST', 'GET'])
@jwt_required
def delete_fcm_token():
    if request.method == 'POST':
        print('inside savefcmtoken POST')
        request_data = request.get_json()
        fcm_token = request_data['fcm_token']
        main_person_id = get_jwt_identity()['id']
        db.session.query(FcmTokens).filter(FcmTokens.token == fcm_token).filter(FcmTokens.person_id == str(main_person_id)).delete()
    return jsonify({"message": 'delete fcm token'}), 200


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


@app.route('/interactedusers', methods=['POST', 'GET'])
@jwt_required
def interactedusers():
    # TODO Check if the users were at the same point within 3 seconds
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


@app.route('/interactionnotification', methods=['POST', 'GET'])
@jwt_required
def interaction_notification():
    '''
    fetch all users from interacted table and give them push
    notification that they came in contact in person
    who had symptoms/infection
    '''
    if request.method == 'POST':
        request_data = request.get_json(force=True)
        person_condition = request_data['person_condition']
        main_person_id = get_jwt_identity()['id']

        # below query gives us every user he interacted except himself, safe to notify everyone
        # interacted_users_within_15_days = db.session.query(InteractedUsers.interacted_id, InteractedUsers.at_time).filter(InteractedUsers.person_id==main_person_id).filter(InteractedUsers.interacted_id!=main_person_id).all()
        interacted_users_within_15_days = db.session.query(InteractedUsers.interacted_id).filter(InteractedUsers.person_id==main_person_id).filter(InteractedUsers.interacted_id!=main_person_id).all()

        print(interacted_users_within_15_days)
        interacted_user_ids_within_15_days = [x[0] for x in interacted_users_within_15_days]
        
        # interacted_user_time_within_15_days = [str(x[1]) for x in interacted_users_within_15_days]
        # print(interacted_user_time_within_15_days)
        
        # interacted_user_condition_within_15_days = [str(x[1]) for x in interacted_user_ids_within_15_days]

        interacted_users_token_list = []
        interacted_users_tokens = db.session.query(FcmTokens.token).filter(FcmTokens.person_id == func.any(interacted_user_ids_within_15_days)).all()
        interacted_users_token_list = [x[0] for x in interacted_users_tokens]

        # TODO dispatch interacted_users_token_list and message to celery for
        # sending push notification using fcm and use person_condition

        # TODO remove for loop, its just for checking
        for token in interacted_users_token_list:
            print(token)

        # TODO we can send to everyone but for testing send to one
        # thats present but send with celery
        message_body = ""
        if person_condition == "sysmptoms":
            message_body = "Hi!, you contacted someone having {} of Corona Virus".format(person_condition)
        else:
            message_body = "Hi!, you contacted someone having who were potentially infected with Corona Virus as\
confirmed by the user you interacted".format(person_condition)

        registration_id = "d8hJT99CQpk:APA91bHAQS9KIaJbSIndKq5ep2zntKjnSbDQViSkOQ5MehvqI6xInL8-t4TCmLStxjHHZXZS8aOfYuiQ1uBXX-rAhZTEMQNVI7NIXiCiVi7p1R3DKb7bra38TPpro8yBxGlsa9CNmOrT"
        message_title = "from dodge corona"
        message_body = "Hi, you contacted someone with " + person_condition
        result = push_service.notify_single_device(registration_id=registration_id,
                                                   message_title=message_title,
                                                   message_body=message_body,
                                                   low_priority=False,
                                                   )
        print(result)

        '''
        # Send to multiple devices by passing a list of ids.
        registration_ids = ["<device registration_id 1>", "<device registration_id 2>", ...]
        message_title = "Uber update"
        message_body = "Hope you're having fun this weekend, don't forget to check today's news"
        result = push_service.notify_multiple_devices(registration_ids=registration_ids, message_title=message_title, message_body=message_body)
        '''
        return jsonify({'hello': 'world'})
    return jsonify({'hello': 'world'})


@app.route('/', methods=['GET'])
def landingpage():
    if request.method == 'GET':
        print('inside /')
        return flask.send_from_directory("web/", 'index.html')
    return flask.send_from_directory("web/", 'index.html')
    #     return jsonify({'hello': 'world'})
    # return jsonify({'hello': 'world'})


# @cross_origin()
@app.route('/subscribepublic', methods=['POST'])
def subscribe_for_public_info():
    if request.method == 'POST':
        print('inside /subscribepublic')
        data = request.get_json(force=True)
        email = data['email']
        if email:
            print(str(email))
            email_in_db = db.session.query(Subscribe.email).filter(Subscribe.email==str(email)).first()
            if email_in_db:
                return jsonify({'hello': 'world'})
            subscribe_user = Subscribe(email)
            db.session.add(subscribe_user)
            db.session.commit()
        else:
            print('not email')
        # TODO implement subscribtion of email, store it in the db
        # unique email and also create one for deletion
        return jsonify({'hello': 'world'})
    return jsonify({'hello': 'world'})


# @cross_origin()
@app.route('/feedback', methods=['POST'])
def feedback():
    print(' not in POST')
    if request.method == 'POST':
        print('inside /feedback')
        data = request.get_json(force=True)
        name = data['name']
        email = data['email']
        subject = data['subject']
        message = data['message']
        print(name)
        print(email)
        print(subject)
        print(message)
        if email:
            print(str(email))
            feedback_user = Feedback(name, email, subject, message)
            db.session.add(feedback_user)
            db.session.commit()
        else:
            print('not email')
        # TODO push feedback to db
        # TODO also implement a page to read feedback for admin only
        # unique email and also create one for deletion
        return jsonify({'hello': 'world'})
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


'''

SERVER as static website
python3 -m http.server

'''
