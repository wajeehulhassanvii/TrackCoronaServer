from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, AdminIndexView
from flask_login import current_user, AnonymousUserMixin
from flask import redirect, url_for

from extensions import app
from extensions import db

# import admin panel
from models.user import User
from models.interactedusers import InteractedUsers
from models.lastlocationpostgis import LastLocationPostGis
from models.userhealth import UserHealth


class MyModelView(ModelView):
    can_create = True
    can_edit = True
    can_delete = True
    
    def is_accessible(self):
        ''' In this method we check if user can view ModelView'''
        # currently true because current_user is authenticated
        # control true or false, easily be done using flask_security
        # user_email = db.session.query(User.email).first()
        user_email = None
        if current_user.is_authenticated:
            user_email = current_user.email
        else :
            return False
        check = False;
        if user_email == "waji@gmail.com":
            check = True
        else:
            check = False
        # return current_user.is_authenticated
        return check

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('/login'))


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        ''' In this method we check if user can view ModelView'''
        # currently true because current_user is authenticated
        # control true or false, easily be done using flask_security
        # user_email = db.session.query(User.email).first()
        user_email = None
        if current_user.is_authenticated:
            user_email = current_user.email
        else :
            return False
        check = False;
        if user_email == "waji@gmail.com":
            check = True
        else:
            check = False
        # return current_user.is_authenticated
        return check

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('/login'))


# initialize admin with bootstrap3
# admin = Admin(app, template_mode="bootstrap3", index_view=MyAdminIndexView())
admin = Admin(app, template_mode="bootstrap3")
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(InteractedUsers, db.session))
admin.add_view(MyModelView(LastLocationPostGis, db.session))
admin.add_view(MyModelView(UserHealth, db.session))

'''
Customize admin for admin only
- create own class for modelview
- inherit from existing ModelView as MyModelView
- now from inherited model we can customize anything from modelview
- if is_accessible function 'overriden' returns true then admin
- otherwise no
- change the business logic and login the correct user
'''
