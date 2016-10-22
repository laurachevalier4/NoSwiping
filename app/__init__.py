import os
from flask import Flask
from flask.json import JSONEncoder
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, current_user
from flask.ext.babel import Babel, lazy_gettext
# import model, views

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

from app import views, model

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

@app.before_first_request
def before_first_request():
    user_datastore = app.security.datastore
    testuser1 = {
        'name': 'Laura Chevalier',
        'username': 'LauraIsCool',
        'password': 'secretcode'
    }

    testuser2 = {
        'name': 'Vincent Chov',
        'username': 'VincentIsCool2',
        'password': 'muffin'
    }

    if not user_datastore.get_user(testuser1['email']):
        user_datastore.create_user(**user1)

    if not user_datastore.get_user(testuser2['email']):
        user_datastore.create_user(**user2)

    db.session.commit()

if os.environ.get('HEROKU') is not None:
    import logging
    stream_handler = logging.StreamHandler()
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('lending and borrowing setup')
