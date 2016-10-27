from flask.ext.wtf import Form
from flask.ext.babel import gettext
from wtforms import StringField, PasswordField, IntegerField, ValidationError, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Regexp, NumberRange, EqualTo, Required
from .model import User

from flask_security.forms import RegisterForm, ConfirmRegisterForm
from flask_security import current_user
from flask_security.utils import verify_password

class SearchForm(Form):
    search = StringField('search', validators=[DataRequired()])


class UniqueEmail(object):
    def __init__(self, message="Email exists"):
        self.message = message

    def __call__(self, form, field):
        if current_app.security.datastore.find_user(email=field.data):
            raise ValidationError(self.message)


class UniqueUsername(object):
    def __init__(self, message="Username exists"):
        self.message = message

    def __call__(self, form, field):
        if current_app.security.datastore.find_user(username=field.data):
            raise ValidationError(self.message)


class ExtendedRegisterForm(RegisterForm):
    username = StringField('Username', [DataRequired(), Length(min=3, max=50),
                                        Regexp(r'^[A-Za-z0-9.]+$', message='Username contains invalid characters'),
                                        UniqueUsername(message='Username taken')
                                        ])
    terms = BooleanField('Accept TOS', [DataRequired(message='You must accept the TOS')])


class ExtendedConfirmForm(ConfirmRegisterForm):
    username = StringField('Username', [DataRequired(), Length(min=3, max=50),
                                        Regexp(r'^[A-Za-z0-9.]+$', message='Username contains invalid characters'),
                                        UniqueUsername(message='Username taken')
                                        ])
    terms = BooleanField('I accept the TOS', [Required()])
