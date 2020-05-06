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
        user_email = db.session.query(User.email).first()
        check = False;
        if user_email == "waji@gmail.com":
            print('user is waji, should be accessible')
            check = True
        else:
            check = False
        # return current_user.is_authenticated
        return check

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('/login'))


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        ''' In this method we check if user can view AdminVIew'''
        # currently true because current_user is authenticated
        # control true or false, easily be done using flask_security
        user_email = db.session.query(User.email).first()
        check = False;
        if user_email == "waji@gmail.com":
            print('user is waji, should be accessible')
            check = True
        else:
            check = False
        # return current_user.is_authenticated
        return check

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('/login'))


# initialize admin with bootstrap3
# admin = Admin(app, template_mode="bootstrap3", index_view=MyAdminIndexView())
# admin.add_view(MyModelView(User, db.session))
admin = Admin(app, template_mode="bootstrap3")


'''
Customize admin for admin only
- create own class for modelview
- inherit from existing ModelView as MyModelView
- now from inherited model we can customize anything from modelview
- if is_accessible function 'overriden' returns true then admin
- otherwise no
- change the business logic and login the correct user
'''
