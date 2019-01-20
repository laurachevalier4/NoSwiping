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
    listings = db.relationship('Listing', backref='owner', lazy='dynamic', \
        foreign_keys='Listing.owner_id')
    borrows = db.relationship('Listing', backref='borrower', lazy='dynamic', \
        foreign_keys='Listing.borrower_id')
    notifications = db.relationship('Notification', backref='user', \
        lazy='dynamic', foreign_keys='Notification.user_id')

    def __repr__(self):
        return str(self.username)

    def get_listings(self, borrower_or_owner):
        if (borrower_or_owner == "owner"):
            return Listing.query.all().filter(Listing.owner_id == self.id)
        else:
            return Listing.query.all().filter(Listing.borrower_id == self.id)

    """
    def __init__(self, name, username, password, email, location):
        self.name = name
        self.username = username
        self.email = email
        self.password = password
        self.location = location
    """

    def get_latest_notifications(self):
        return self.notifications.order_by(Notification.timestamp.desc()) \
            .limit(10)

    def get_all_notifications(self):
        return self.notifications.order_by(Notification.timestamp.desc()).all()

    def get_unread_notifications(self):
        return self.notifications.filter(Notification.acked == False) \
            .order_by(Notification.timestamp.desc()).all()

    def user_listings(self):
        # return listings (selling) for given user
        return self.listings.order_by(Listing.date_listed.desc()).limit(10)

    def user_borrows(self):
        return self.borrows.order_by(Listing.date_listed.desc()).limit(10)

    def borrow_listing(self, listing):
        self.borrows.append(listing)
        self.points -= listing.cost

    def return_listing(self, listing):
        self.borrows.remove(listing)

    def lend_listing(self, listing):
        self.points += listing.cost

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
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner_username = db.Column(db.String(255), db.ForeignKey('user.username'))
    borrower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    borrower_username = db.Column(db.String(255), db.ForeignKey('user.username'), \
        nullable=True)
    title = db.Column(db.String(255), unique=True, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    cost = db.Column(db.Integer, nullable=True)
    location = db.Column(db.Integer)
    date_listed = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    date_borrowed = db.Column(db.DateTime, nullable=True)

    def __init__(self, owner_id, owner_username, title, category, cost, \
        borrower_id=None, borrower_username=None, date_borrowed=None):
        self.owner_id = owner_id
        self.owner_username = owner_username
        self.borrower_id = borrower_id
        self.borrower_username = borrower_username
        self.title = title
        self.category = category
        self.cost = cost
        self.date_borrowed = date_borrowed

    def serialize(self, columns):
        cols = {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'cost': self.cost,
            'location': self.location,
            'date_listed': dump_datetime(self.date_listed),
            'owner_id' : self.owner_id,
            'borrower_id': self.borrower_id
        }
        return {col: cols.get(col, None) for col in columns}

    def mark_borrowed(self, borrower):
        self.borrower_id = borrower.id
        self.borrower_username = borrower.username
        self.date_borrowed = datetime.datetime.utcnow()

    def mark_returned(self):
        self.borrower_id = None
        self.borrower_username = None
        self.date_borrowed = None

if enable_search:
    whooshalchemy.whoosh_index(app, Listing)

class Notification(db.Model):
    __tablename__ = 'notification'

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_username = db.Column(db.String(255), db.ForeignKey('user.username'), \
        nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    acked = db.Column(db.Integer, default=0)  # has user seen this notification?

    def __init__(self, message, user_id, user_username):
        self.message = message
        self.user_id = user_id
        self.user_username = user_username
