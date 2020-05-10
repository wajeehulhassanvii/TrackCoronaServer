from flask import Flask
from flask import session

from flask_migrate import Migrate
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager

from flask_bcrypt import Bcrypt
from flask_json import FlaskJSON, JsonError, json_response, as_json

from flask_sqlalchemy import SQLAlchemy
import datetime

from flask_mail import Mail
from pyfcm import FCMNotification
 
from flask_jwt_extended import (JWTManager, jwt_required,
                                jwt_refresh_token_required,
                                jwt_optional, fresh_jwt_required,
                                get_raw_jwt, get_jwt_identity,
                                create_access_token, create_refresh_token,
                                set_access_cookies, set_refresh_cookies,
                                unset_jwt_cookies, unset_access_cookies)

from celery import Celery
from flask_cors import CORS

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

# Configure application with config file in root directory named config.cfg
app = Flask(
    __name__,
    static_url_path='',
            static_folder='web',
            template_folder='web',
            # template_folder="web",
    )  # Flask app ends here
app.config.from_pyfile('config.cfg')
# app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(minutes=1)
# Setup the flask-jwt-extended extension. See:
ACCESS_EXPIRES = datetime.timedelta(seconds=30)
REFRESH_EXPIRES = datetime.timedelta(days=5)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = ACCESS_EXPIRES
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = REFRESH_EXPIRES



# INITIALIZE DIFFERENT GLOBAL VARIABLES
json = FlaskJSON(app)
# initialize toolbar
toolbar = DebugToolbarExtension()

# initialize Flask login manager
login_manager = LoginManager()
login_manager.init_app(app)

# take us to login page if we are not logged in and try to visit protected page
login_manager.login_view = '/login'
login_manager.login_message = 'please! login in first...'
login_manager.fresh_view = '/login'
login_manager.needs_refresh_message = 'login in again please!!!'

#initialize flask mail
mail = Mail(app)

# initialize bcrypt
bcrypt = Bcrypt(app)
# initialize database migration management

# initialize the database connection
db = SQLAlchemy(app)

# import migrate
migrate = Migrate(app, db)

# initialize JWT
jwt = JWTManager(app)

CORS(app)

# proxy_dict = {
#         #   "http": "http://127.0.0.1",
#         #   "https": "http://127.0.0.1",
#           "http": "http://10.0.2.2",
#           "https": "http://10.0.2.2",
#         }

push_service = FCMNotification(api_key="AAAA0eHajjA:APA91bF78pTIEpZKn3EkWAqsua8FNx-6kj3t9g-21Mv5IbFZhiuIlfsNPRPq8jl802KtLNUWCBFd5fj0glA4DxnaQxGeoed2CN_HYo2qQbNRUfq48gybH0qWE0pYM0YvQY7Bx6MHbavo")
    #                             #    proxy_dict=proxy_dict
# )

# initialize Celery
def make_celery(app):
    celery = Celery(
        app.name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

# celery = Celery(app.name,
#                 broker=app.config['CELERY_BROKER_URL'],
#                 # include=['update_health_with_celery', 'update_location_with_celery']
#                 )
# celery.conf.update(app.config)
# app.autodiscover_tasks()

celery = make_celery(app)

from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()

