from extensions import db
from extensions import app
from extensions import jwt

# import model classes to create the tables
from models import user
from models import lastlocationpostgis
from models import userhealth
from models import token_blacklist
from models import interactedusers
from models import fcm_tokens
from models import subscribe
from models import feedback

# create dbs
db.create_all()
db.session.commit()

# create admin and other users here in database as:
'''
admin = User(username='admin', email='admin@example.com')
>>> guest = User(username='guest', email='guest@example.com')
'''

# import view apis
import views   # noqa: E402
import myadmin

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
    # app.run(host='127.0.0.1', port=8000, debug=True)
