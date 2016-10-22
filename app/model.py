import datetime
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import select, func, or_, and_
from app import db

def dump_datetime(value):
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(120))
    about_me = db.Column(db.String(255))
    location = db.Column(db.Integer)
    points = db.Column(db.Integer)
    listings = db.relationship('Listing', backref='user', lazy='dynamic')
    purchased_listings = db.relationship('Listing', backref='user', lazy='dynamic')

    def __repr__(self):
        return str(self.username)

    def __init__(self, name, username, password, location):
        self.name = name
        self.username = username
        self.email = email
        self.password = password
        self.location = location

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
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    cost = db.Column(db.Integer, nullable=True)
    location = db.Column(db.Integer)
    date_listed = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column('User', db.ForeignKey('user.id'))
    buyer_id = db.Column('User', db.ForeignKey('user.id'))

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
