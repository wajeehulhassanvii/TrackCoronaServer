
from extensions import app
from extensions import db
from extensions import session
from extensions import login_manager

from flask import jsonify, request
from flask_login import logout_user
from flask_login import current_user
from flask_login import login_user
from flask_login import login_required
from flask_login import fresh_login_required

# from geoalchemy2 import ST_DFullyWithin
# from geoalchemy2 import WKBElement
# from geoalchemy2 import WKSpatialElement
# from geoalchemy2.functions import functions
# from sqlalchemy import func

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
            remember_me = request_data['rememberMe']
            print('email {}'.format(email))
            print(str(user))
            if user is not None:
                password = request_data['password']
                if user.check_password(password):
                    db.session.add(user)
                    db.session.commit()
                    login_user(user, remember=remember_me)
                    session['logged_in'] = True
                    if session.get('logged_in'):
                        if session['logged_in'] is True:
                            print('from session' + str(session["logged_in"]))
                            print(current_user)
                    # load_user(user.id)
                    return jsonify({"message": str("login\
                        successful")}), 200
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


@app.route('/checkcurrentuser')
def check_current_user():
    if current_user:
        print('{}'.format(current_user.email))
        return current_user.email
    return 'no user'


@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""
    if user_id is not None:
        return User.query.get(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    print(' user not loaded')
    return jsonify({"message": str("did not loaded\
        user")}), 200


@app.route('/logout', methods=['GET'])
# @login_required
def logout():
    print('clearing user login from sessions')
    # session['logged_in'] = False
    user = current_user
    user.is_authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return jsonify({"message": str("you are logged\
        out\nstay home stay safe!!!")}), 401


@app.route('/getuserswithindiameter', methods=['POST', 'GET'])
@login_required
def get_users_within_diameter():
    '''
    get the geocoordinates of all the people in close proximity
    error-> 302: redirect when no login, otherwise success : 200
    '''
    if request.method == 'POST':
        if session.get('logged_in'):
            if session['logged_in'] is True:
                print(current_user)
        else:
            print('not in session')
        request_data = request.get_json(force=True)
        print('inside post')
        userActive = True
        try:
            main_user_latitude = request_data['userLatitude']
            main_user_longitude = request_data['userLongitude']
            # user_point_geoalchemy = func.Geometry(func.ST_GeographyFromText('POINT({} {})'.format(main_user_longitude, main_user_latitude)))

            # we will convert the kilometer distance into degrees
            # distance = d * 0.014472
            # 111.32 km/degree (the accepted figure is 111.325 km).
            # #1 mile = 0.014472 degrees
            # wkb_point = WKBSpatialElement( buffer( point.wkb ), 4326 )
            # INSERT OR UPDATE THE USER LOCATION AND ITS CURRENT STATUS
            print(current_user)
            if current_user:
                print('there is a user {}'.format(current_user))
            # print(LastLocationPostGis.query.filter(user_id=current_user.id))
            # if count_user:
            #     # here insert the lastlocation because the location doesn't exist
            #     last_location = LastLocationPostGis(user_point_geoalchemy, main_user_active)
            #     db.session.add(last_location)
            #     db.session.commit()
            # users = db.query(LastLo).\
            #     filter(func.ST_DWithin(User.location,  wkb_element, distance)).all()
            print('function complete inside try block')
            return jsonify({"message": str("in side post")}), 200
        except KeyError as err:
            print(err)
            return jsonify({"message": str(err)}), 400

    return jsonify({"message": str("you are in a protected area")}), 200


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


'''
