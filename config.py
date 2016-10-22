import os, logging
from app import helpers
basedir = os.path.abspath(os.path.dirname(__file__))

LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOGGING_LOCATION = 'log.log'
LOGGING_LEVEL = logging.DEBUG

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = ('sqlite:///' + os.path.join(basedir, 'app.db') +
                               '?check_same_thread=False')
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_RECORD_QUERIES = True
WHOOSH_BASE = os.path.join(basedir, 'search.db')
# Not sure what WHOOSH is...

def configure_app(app):
    config_name = os.getenv('FLASK_CONFIGURATION', 'default')
    print "Running " + str(config_name) + " environment."
    app.jinja_env.filters['format_md5'] = helpers.format_md5
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    """app.security = Security(app,
                            user_datastore,
                            confirm_register_form=forms.ExtendedConfirmForm,
                            register_form=forms.ExtendedRegisterForm)"""

# slow database query threshold (in seconds)
DATABASE_QUERY_TIMEOUT = 0.5

# administrator list
ADMINS = ['lmc.613@nyu.edu']

LISTINGS_PER_PAGE = 20
MAX_SEARCH_RESULTS = 20
