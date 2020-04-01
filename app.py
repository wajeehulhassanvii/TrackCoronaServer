from extensions import db
from extensions import app

# import model classes to create the tables
from models import user
from models import lastlocationpostgis
from models import userhealth

# create dbs
db.create_all()
db.session.commit()

# import view apis
import views   # noqa: E402
import myadmin
if __name__ == '__main__':
    app.run(host='127.0.0.1',port=8000,debug=True)
