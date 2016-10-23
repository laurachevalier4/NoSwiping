from flask.ext.wtf import Form
from flask.ext.babel import gettext
from wtforms import StringField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length
from .model import User

class SearchForm(Form):
    search = StringField('search', validators=[DataRequired()])
