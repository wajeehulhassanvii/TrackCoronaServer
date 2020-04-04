from flask import Flask
from flask import session

from flask_migrate import Migrate
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager

from flask_bcrypt import Bcrypt

from flask_sqlalchemy import SQLAlchemy
import datetime

from flask_jwt_extended import (JWTManager, jwt_required,
                                jwt_refresh_token_required,
                                jwt_optional, fresh_jwt_required,
                                get_raw_jwt, get_jwt_identity,
                                create_access_token, create_refresh_token,
                                set_access_cookies, set_refresh_cookies,
                                unset_jwt_cookies, unset_access_cookies)

# Configure application with config file in root directory named config.cfg
app = Flask(
    __name__,
    # insert names below like ->template_folder="../client/templates",<-
    )  # Flask app ends here
app.config.from_pyfile('config.cfg')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)


# INITIALIZE DIFFERENT GLOBAL VARIABLES

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


# initialize bcrypt
bcrypt = Bcrypt(app)
# initialize database migration management

# initialize the database connection
db = SQLAlchemy(app)

# import migrate
migrate = Migrate(app, db)

# initialize JWT
jwt = JWTManager(app)
