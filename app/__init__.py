import os
from flask import Flask
from flask.json import JSONEncoder
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel, lazy_gettext
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required
from werkzeug.security import generate_password_hash
import babel as b

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)
lm = LoginManager(app)

from app import views, model
from model import User, Role

lm.login_view = 'login'
lm.login_message = lazy_gettext('Please log in to access this page.')
# TODO: Figure out login w/o using OpenID like Miguel does
babel = Babel(app)

def format_datetime(value, format='medium'):
    if format == 'full':
        format="EEEE, d MMMM y 'at' HH:mm"
    elif format == 'medium':
        format="EE dd.MM.y HH:mm"
    return b.dates.format_datetime(value, format)

app.jinja_env.filters['datetime'] = format_datetime

class CustomJSONEncoder(JSONEncoder):
    """This class adds support for lazy translation texts to Flask's
    JSON encoder. This is necessary when flashing translated texts."""
    def default(self, obj):
        from speaklater import is_lazy_string
        if is_lazy_string(obj):
            try:
                return unicode(obj)  # python 2
            except NameError:
                return str(obj)  # python 3
        return super(CustomJSONEncoder, self).default(obj)

app.json_encoder = CustomJSONEncoder

# Setup Flask_Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

@app.before_first_request
def before_first_request():
    db.drop_all()
    db.create_all()

    testuser2 = {
        'name': 'Laura Chevalier',
        'username': 'LauraIsCool',
        'password_hash': generate_password_hash('secretcode'),
        'email': 'xxx@nyu.edu',
        'active': True,
        'points': 20
    }

    testuser3 = {
        'name': 'Vincent Chov',
        'username': 'VincentIsCool2',
        'password_hash': generate_password_hash('muffin'),
        'email': 'yyy@nyu.edu',
        'active': True,
        'points': 10
    }

    user_datastore.find_or_create_role(
        name='admin', description='Administrator')
    user_datastore.find_or_create_role(name='user', description='End user')

    db.session.commit()

    if not user_datastore.get_user(testuser2['email']):
        user_datastore.create_user(**testuser2)

    if not user_datastore.get_user(testuser3['email']):
        user_datastore.create_user(**testuser3)

    db.session.commit()

    user_datastore.add_role_to_user(testuser2['email'], 'user')
    user_datastore.add_role_to_user(testuser3['email'], 'admin')

    db.session.commit()

    testListing1 = {
        'owner_id' : 1,
        'borrower_id' : 2,
        'owner_username': 'LauraIsCool',
        'borrower_username': 'VincentIsCool2',
        'title' : 'Cast of Jersey Shore',
        'category' : 'Tools',
        'cost' : 1
    }

    listing1 = model.Listing(**testListing1)
    db.session.add(listing1)
    db.session.commit()

    testListing2 = {
        'owner_id' : 2,
        'borrower_id' : 1,
        'owner_username': 'VincentIsCool2',
        'borrower_username': 'LauraIsCool',
        'title' : 'My Little Pony',
        'category' : 'Games',
        'cost' : 30
    }

    listing2 = model.Listing(**testListing2)
    db.session.add(listing2)
    db.session.commit()

    testListing3 = {
        'owner_id' : 2,
        'borrower_id' : None,
        'owner_username': 'VincentIsCool2',
        'borrower_username': None,
        'title' : 'Magic Bullet',
        'category' : 'Kitchenware',
        'cost' : 20
    }

    listing3 = model.Listing(**testListing3)
    db.session.add(listing3)
    db.session.commit()

    testListing4 = {
        'owner_id' : 1,
        'borrower_id' : None,
        'owner_username': 'LauraIsCool',
        'borrower_username': None,
        'title' : 'Made to Stick',
        'category' : 'Books',
        'cost' : 10
    }

    listing4 = model.Listing(**testListing4)
    db.session.add(listing4)
    db.session.commit()

if os.environ.get('HEROKU') is not None:
    import logging
    stream_handler = logging.StreamHandler()
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('lending and borrowing setup')
