from flask_wtf import FlaskForm
from flask_babel import gettext
from wtforms import StringField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length
from .model import User

class SearchForm(FlaskForm):
    search = StringField('search', validators=[DataRequired()])
