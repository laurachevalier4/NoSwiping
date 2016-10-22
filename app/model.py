import datetime
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from flask.ext.security import UserMixin, RoleMixin
from sqlalchemy import select, func, or_, and_
from app import db

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
    password = db.Column(db.String(120))
    about_me = db.Column(db.String(255))
    location = db.Column(db.Integer)
    points = db.Column(db.Integer)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return str(self.username)

    def get_listings(self, buyer_or_seller):
        if (buyer_or_seller == "seller"):
            return Listing.query.filter(Listing.seller_id == self.id)
        else:
            return Listing.query.filter(Listing.buyer_id == self.id)

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

class Listing(db.Model):
    __tablename__ = 'listing'

    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer)
    buyer_id = db.Column(db.Integer)
    title = db.Column(db.String(255), unique=True, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    cost = db.Column(db.Integer, nullable=True)
    location = db.Column(db.Integer)
    date_listed = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def filtered_listings(self, category, location=None):
        # return a filtered list of 20 listings based on category and location
        results = Listing.query.filter(and_(Listing.category == category, _or(Listing.location == location, location == None))).order_by(Listing.date_listed.desc()).limit(20)

    def serialize(self, columns):
        cols = {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'cost': self.cost,
            'location': self.location,
            'date_listed': dump_datetime(self.date_listed),
            'user_id': self.user_id
        }
        return {col: cols.get(col, None) for col in columns}
