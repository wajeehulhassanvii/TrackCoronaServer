from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, AdminIndexView
from flask_login import current_user
from flask import redirect, url_for

from extensions import app
from extensions import db

# import admin panel
from models.user import User


class MyModelView(ModelView):
    def is_accessible(self):
        ''' In this method we check if user can view ModelView'''
        # currently true because current_user is authenticated
        # control true or false, easily be done using flask_security
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('/login'))


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        ''' In this method we check if user can view AdminVIew'''
        # currently true because current_user is authenticated
        # control true or false, easily be done using flask_security
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('/login'))


# initialize admin with bootstrap3
# admin = Admin(app, template_mode="bootstrap3", index_view=MyAdminIndexView())
admin = Admin(app, template_mode="bootstrap3")
admin.add_view(MyModelView(User, db.session))


'''
Customize Armin for admin only
- create own class for modelview
- inherit from existing ModelView as MyModelView
- now from inherited model we can customize anything from modelview
- if is_accessible function 'overriden' returns true then admin
- otherwise no
- change the business logic and login the correct user
'''
