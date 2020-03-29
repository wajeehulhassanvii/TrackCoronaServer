from extensions import app
from flask_login import login_manager
from flask_login import logout_user
from flask_login import current_user
from flask_login import login_user
from flask_login import login_required
from flask import render_template
from flask import session, redirect, jsonify, request
from models.user import User


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


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return 'you are now loged out'


@login_required
@app.route('/onlyForLoginInUser')
def onlyForLoginInUser():
    return 'you must be logged in {},\
        current_user is user object'.format(current_user)


@app.route('/register', methods=['GET'])
def view_registration_form():
    return render_template('guest_registration.html')


@app.route('/login', methods=['GET', 'POST'])
def loginUser():
    if request.method == 'POST':
        personEmail = request.json['email']
        person = User.query.filter_by(email=personEmail).first()
        if not person:
            return 'person does not exist in database'
        login_user(person)

        if 'next' in session:
            next = session['next']
            return redirect(next)
        return 'you are now logged in'

    if request.method == 'GET':
        session['next'] = request.args.get('next')
        return 'take user to login page'


# @app.route('/register', methods=['POST'])
# def register_guest():
#     from models import Guest
#     name = request.form.get('name')
#     email = request.form.get('email')

#     guest = Guest(name, email)
#     db.session.add(guest)
#     db.session.commit()

    # return render_template(
    #     'guest_confirmation.html', name=name, email=email)

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


def testImport():
    print('imported successfully')