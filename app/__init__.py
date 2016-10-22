import os
from flask import Flask
from flask.json import JSONEncoder
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, current_user
from flask.ext.babel import Babel, lazy_gettext
from flask.ext.security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

from app import views, model
from model import User, Role

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
lm.login_message = lazy_gettext('Please log in to access this page.')
# TODO: Figure out login w/o using OpenID like Miguel does
babel = Babel(app)


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
        'password': 'secretcode',
        'email': 'xxx@nyu.edu',
        'active': True
    }

    testuser3 = {
        'name': 'Vincent Chov',
        'username': 'VincentIsCool2',
        'password': 'muffin',
        'email': 'yyy@nyu.edu',
        'active': True
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
        'seller_id' : 1,
        'buyer_id' : 2,
        'title' : 'Free pet therapy session',
        'category' : 'therapy'
    }

    listing1 = model.Listing(**testListing1)
    db.session.add(listing1)
    db.session.commit()

    testListing2 = {
        'seller_id' : 3,
        'buyer_id' : 4,
        'title' : 'Buying time',
        'category' : 'services'
    }

    listing2 = model.Listing(**testListing2)
    db.session.add(listing2)
    db.session.commit()

    testListing3 = {
        'seller_id' : 5,
        'buyer_id' : 6,
        'title' : 'StackOverflow tutoring',
        'category' : 'services'
    }

    listing3 = model.Listing(**testListing3)
    db.session.add(listing3)
    db.session.commit()

if os.environ.get('HEROKU') is not None:
    import logging
    stream_handler = logging.StreamHandler()
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('lending and borrowing setup')
