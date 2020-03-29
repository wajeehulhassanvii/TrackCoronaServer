from flask import Flask

from flask_migrate import Migrate
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager

from flask_bcrypt import Bcrypt

from flask_sqlalchemy import SQLAlchemy

# Configure application with config file in root directory named config.cfg
app = Flask(
    __name__,
    # insert names below like ->template_folder="../client/templates",<-
    )  # Flask app ends here
app.config.from_pyfile('config.cfg')


# INITIALIZE DIFFERENT GLOBAL VARIABLES

# initialize toolbar
toolbar = DebugToolbarExtension()

# initialize Flask login manager
login_manager = LoginManager(app)

# take us to login page if we are not logged in and try to visit protected page
login_manager.login_view = '/login'
login_manager.login_message = 'Cannot login sorry!'

# initialize bcrypt
bcrypt = Bcrypt()
# initialize database migration management

# initialize the database connection
db = SQLAlchemy(app)

# import migrate
migrate = Migrate(app, db)