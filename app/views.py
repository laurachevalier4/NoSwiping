from app import app
from app import model, db
from app.model import User
from flask import render_template, flash, redirect, session, url_for, request, \
    g, jsonify, abort
from flask_login import login_user, logout_user, current_user, \
    login_required
from flask_sqlalchemy import SQLAlchemy
from model import Listing
from urlparse import urlparse, urljoin

from pagination import Pagination, get_listings_for_page, url_for_other_page
from config import MAX_SEARCH_RESULTS
from forms import SearchForm, LoginForm

PER_PAGE = 20       # Number of results per page

@app.before_request
def before_request():
    g.user = current_user
    g.search_form = SearchForm()
    if current_user.is_authenticated:
        g.notifications = current_user.get_unread_notifications()
        # Notifications will only update when user makes new request

# This is the homepage/categories page!
@app.route('/')
@app.route('/index')
@app.route('/categories')
@login_required
def index():
    return render_template("index.html")

# taken from http://flask.pocoo.org/snippets/62/
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

@app.route('/newpost', methods=['GET', 'POST'])
@login_required
def newpost():
    if request.method == 'GET':
        return render_template('newpost.html')
    elif request.method == 'POST':
        print("user posted!")
        title = request.form.get('title')
        print("Title:", str(title))
        value = request.form.get('value')
        print("Value:", int(value))
        category = request.form.get('categories')
        print("Category:", str(category))
        userid = current_user.id
        username= current_user.username
        new_post = model.Listing(owner_id=userid, owner_username=username, title=title, \
            category=category, cost=value)
        db.session.add(new_post)
        db.session.commit()
        post = Listing.query.filter_by(title=title).first()
        print(url_for('index'))
        return redirect(url_for('index'))

# Once you choose a category, show some transactions from that category
@app.route('/categories/<category_name>', defaults={'page': 1})
@app.route('/categories/<category_name>/<int:page>')
@login_required
def category(category_name, page):
    allListings = model.Listing.query.filter_by(category=category_name) \
        .filter(Listing.borrower_id==None).all()
    count = len(allListings)

    listings = get_listings_for_page(page, PER_PAGE, count, allListings)

    if len(listings) < 1 and page != 1:
        # There are no more pages left
        abort(404)

    # Otherwise, create a new page
    pagination = Pagination(page, PER_PAGE, count)
    return render_template('category.html',
                           pagination=pagination,
                           listings=listings,
                           category_name=category_name,
                           num_listings=count)

# The page for a specific transaction
@app.route('/transactions/<transaction_id>')
@login_required
def transaction(transaction_id):
    return "You chose the %s transaction!" % (transaction_id)

@app.route('/search', methods=['POST'])
@login_required
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    return redirect(url_for('search_results', query=g.search_form.search.data))

@app.route('/search_results/<query>')
@login_required
def search_results(query):
    results = model.Listing.query.filter(Listing.borrower_id==None).whoosh_search(query, MAX_SEARCH_RESULTS).all()
    return render_template('search_results.html',
                           query=query,
                           results=results)

@app.route('/listing/<listing_id>')
@login_required
def listing_details(listing_id):
    listing = Listing.query.get(listing_id)
    if not listing:
        return redirect(url_for('index'))
    return render_template('listing_details.html',
                            listing=listing)

@app.route('/profile/')
@app.route('/profile/<user_id>')
@login_required
def profile(user_id=None):
    if user_id is None:
        user = current_user
        print(request.args)
        if request.args.get('borrow_success'):
            flash('Congrats on your new borrow!')
    else:
        user = User.query.get(user_id)
    listings = user.user_listings()
    available_listings = filter(lambda listing: listing.borrower_id is None, listings)
    unavailable_listings = filter(lambda listing: listing.borrower_id is not None, listings)
    borrows = user.user_borrows()
    return render_template('profile.html',
                            user=user,
                            available_listings=available_listings,
                            unavailable_listings=unavailable_listings,
                            borrows=borrows)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    next = request.args.get('next')
    if not is_safe_url(next):
        return flask.url_for('index')
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        print("user: {}".format(user))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(next or url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/borrow', methods=['POST'])
@login_required
def borrow():
    borrower_id = request.args.get('borrower_id')
    owner_id = request.args.get('owner_id')
    listing_id = request.args.get('listing_id')
    current_user_id = str(current_user.id)
    if borrower_id != current_user_id:
        return "Given borrower id is not logged in user id... whatchu tryna do?"
    else:
        try:
            borrower = User.query.filter_by(id=borrower_id).first()
            owner = User.query.filter_by(id=owner_id).first()
            listing = Listing.query.filter_by(id=listing_id).first()
            borrower.borrow_listing(listing)
            owner.lend_listing(listing)
            listing.mark_borrowed(borrower)
            db.session.commit()
            return redirect(url_for('profile', borrow_success=True))
        except Exception as e:
            # TODO better error handling
            print(e)
            return render_template('listing_details.html', listing=listing)

@app.route('/return', methods=['POST'])
@login_required
def return_listing():
    borrower_id = request.args.get('borrower_id')
    owner_id = request.args.get('owner_id')
    listing_id = request.args.get('listing_id')
    current_user_id = str(current_user.id)
    if borrower_id != current_user_id:
        return "Given borrower id is not logged in user id... whatchu tryna do?"
    else:
        try:
            borrower = User.query.filter_by(id=borrower_id).first()
            owner = User.query.filter_by(id=owner_id).first()
            listing = Listing.query.filter_by(id=listing_id).first()
            borrower.return_listing(listing)
            # owner.take_back_listing(listing)
            listing.mark_returned()
            db.session.commit()
            return redirect(url_for('profile', return_success=True))
        except:
            # TODO better error handling
            return render_template('listing_details.html', listing=listing)

@app.route('/mark_notifications_read', methods=['POST'])
@login_required
def mark_notifications_read():
    notifications = g.notifications  # unread notifications
    for n in notifications:
        n.acked = 1
        db.session.add(n)
    db.session.commit()
    return "success"
