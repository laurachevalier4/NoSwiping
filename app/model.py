import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from flask_security import UserMixin, RoleMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import select, func, or_, and_
from app import app, db, lm

# Import whooshalchemy if you can so you can enable search
import sys
if sys.version_info >= (3, 0):
    enable_search = False
else:
    enable_search = True
    import flask_whooshalchemy as whooshalchemy

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

def dump_datetime(value):
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]

roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(),
                                 db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return str(self.name)

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(255))
    location = db.Column(db.Integer)
    points = db.Column(db.Integer)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return str(self.username)

    def get_listings(self, buyer_or_seller):
        if (buyer_or_seller == "seller"):
            return Listing.query.all().filter(Listing.seller_id == self.id)
        else:
            return Listing.query.all().filter(Listing.buyer_id == self.id)

    """
    def __init__(self, name, username, password, email, location):
        self.name = name
        self.username = username
        self.email = email
        self.password = password
        self.location = location
    """

    def user_listings(self):
        # return listings for given user
        return self.listings.filter(Listing.user_id == self.user_id).order_by(Listing.date_listed.desc()).limit(10)

    def serialize(self, columns):
        cols = {
            'id': self.id,
            'name': self.name,
            'username': self.username,
            'password': self.password,
            'about_me': self.about_me,
            'location': self.location,
            'points': self.points,
        }
        return {col: cols.get(col, None) for col in columns}

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Listing(db.Model):
    __tablename__ = 'listing'
    __searchable__ = ['title']

    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer)
    buyer_id = db.Column(db.Integer)
    title = db.Column(db.String(255), unique=True, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    cost = db.Column(db.Integer, nullable=True)
    location = db.Column(db.Integer)
    date_listed = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, seller_id, buyer_id, title, category, cost):
        self.seller_id = seller_id
        self.buyer_id = buyer_id
        self.title = title
        self.category = category
        self.cost = cost

    def serialize(self, columns):
        cols = {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'cost': self.cost,
            'location': self.location,
            'date_listed': dump_datetime(self.date_listed),
            'seller_id' : self.seller_id,
            'buyer_id': self.buyer_id
        }
        return {col: cols.get(col, None) for col in columns}

if enable_search:
    whooshalchemy.whoosh_index(app, Listing)
