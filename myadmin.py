from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin

from extensions import app
from extensions import db

# import admin panel
from models.user import User

# initialize admin with bootstrap3
admin = Admin(app, template_mode="bootstrap3")
# admin.add_view(ModelView(User, db.session))