import os

from flask import Flask, render_template, request, redirect, session
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager, UserMixin, logout_user, login_user, login_required, current_user



# database_uri = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
#     dbuser=os.environ['DBUSER'],
#     dbpass=os.environ['DBPASS'],
#     dbhost=os.environ['DBHOST'],
#     dbname=os.environ['DBNAME']
#)

app = Flask(
    __name__,
    # insert names below like ->template_folder="../client/templates",<-
    ) # Flask app ends here

postgre_database_uri='postgres+psycopg2://wajeeh-machine:Waje3e3h@127.0.0.1:5432/trackcorona'
# app config is updating app settings
app.config.update(
    # TODO: create postgre database uri string that points to db file
    # below are the app settings
    SQLALCHEMY_DATABASE_URI=postgre_database_uri,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SECRET_KEY='ThisIsSecretKeyForFlaskLogin'
)

# initialize Flask login manager
login_manager = LoginManager(app)
# take us to login page if we are not logged in and try to visit protected page
login_manager.login_view = '/login'
login_manager.login_message = 'Cannot login sorry!'
# initialize the database connection
db = SQLAlchemy(app)
# initialize bcrypt
bcrypt = Bcrypt()
# initialize database migration management
migrate = Migrate(app, db)
toolbar = DebugToolbarExtension()

@app.route('/')
def view_registered_guests():
    from .models.User import User
    person = User.query.all()
    # replaced
    #guests = Guest.query.all()
    #return render_template('guest_list.html', guests=guests)
    return 'all user fetched method called'


@login_manager.user_loader
def load_user(user_id):
    return Person.query.get(int(user_id))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return 'you are now loged out'

@login_required
@app.route('/onlyForLoginInUser')
def onlyForLoginInUser():
    return 'you must be logged in {}, current_user is user object'.format(current_user)


@app.route('/register', methods=['GET'])
def view_registration_form():
    return render_template('guest_registration.html')

@app.route('/login', methods=['GET','POST'])
def loginUser():
    if request.method == 'POST':
        personEmail = request.json['email']
        person = Person.query.filter_by(email=personEmail).first()
        if not person:
            return 'person does not exist in database'
        login_user(person)

        if 'next' in session:
            next = session['next']
            return redirect(next)
        return 'you are now logged in'

    if request.method == 'GET':
        session['next']=request.args.get('next')
        return 'take user to login page'


@app.route('/register', methods=['POST'])
def register_guest():
    from models import Guest
    name = request.form.get('name')
    email = request.form.get('email')

    guest = Guest(name, email)
    db.session.add(guest)
    db.session.commit()

    return render_template(
        'guest_confirmation.html', name=name, email=email)
