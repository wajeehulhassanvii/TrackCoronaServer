
from extensions import login_manager
from flask_login import logout_user
from flask_login import current_user
from flask_login import login_user
from flask_login import login_required
from flask_login import fresh_login_required
from flask import render_template
from flask import session, redirect, jsonify, request
import datetime as dt

from extensions import app
from extensions import db

from models.user import User
from flask_bcrypt import generate_password_hash


@app.route('/')
def view_registered_guests():
    # from models.User import User
    # person = User.query.all()
    # replaced
    # guests = Guest.query.all()
    # return render_template('guest_list.html', guests=guests)
    return 'all user fetched method called'


# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))


@login_required
@app.route('/onlyForLoginInUser')
def onlyForLoginInUser():
    return 'you must be logged in {},\
        current_user is user object'.format(current_user)


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
            db_data = User.query.filter_by(email=email).first()
            print('email {}'.format(email))
            if db_data is not None:
                password = str(request_data['password'])
                if db_data.check_password(password):
                    session['logged_in'] = True
                    # load_user(email)
                    # login_user(db_data)
                    return jsonify({"message": str("login\
                     successful")}), 200
            else:
                return jsonify({"message": str("email\
                     does not have any associated account")}), 400
        except KeyError as err:
            print(err)
            return jsonify({"message": str("Key Error\
                during login")}), 400
        return jsonify({"message": str("Account successfully created")}), 200

    if request.method == 'GET':
        print('inside get method')
        return jsonify({"message": str("GET login\
        function working")}), 200


@login_manager.user_loader
def load_user(email):
    return User.query.filter_by(email=email).first()


@login_required
@app.route('/protectedroute', methods=['POST', 'GET'])
def protected_route():
    return jsonify({"message": str("you are in protected area")}), 200


@app.route('/sendFakeData', methods=['POST', 'GET'])
def sendFakeData():
    if request.method == 'POST':
        ret = {
            'object': 'user',
            'action': 'login',
            # 'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'payload': []
        }
        print('data {}'.format(request))
        data = request.get_json(force=True)
        print('data {}'.format(data))
        if data is None:
            print('no data found akhi')
            return jsonify(), 400
        else:
            try:
                email = data['email']
                person = User.query.filter_by(email=email).first()
                if person is None:
                    person = 'no person found in database'
                password = data['password']
            except KeyError as err:
                print(err)
                return jsonify(ret), 400
        return jsonify({"message": str("post function working\
            {} and {} and {}".format(email, password, person))})

    if request.method == 'GET':
        return jsonify({"message": str("GET function working")})


@app.route('/logout')
@login_required
def logout():
    session['logged_in'] = False
    logout_user()
    return jsonify({"message": str("you are logged out\nstay home stay safe!!!")})


@app.route('/fresh_login')
def fresh_login():
    ''' requires fresh login for user account value modification'''
    return jsonify({"message": str("Fresh Login!!!")})


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
