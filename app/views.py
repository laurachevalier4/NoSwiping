from app import app
from app import model, db
from flask import render_template, flash, redirect, session, url_for, request, \
    g, jsonify, abort
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import login_required, current_user
from model import Listing

from pagination import Pagination, get_listings_for_page, url_for_other_page
from config import MAX_SEARCH_RESULTS
from datetime import datetime
from forms import SearchForm

PER_PAGE = 20       # Number of results per page

@app.before_request
def before_request():
    g.user = current_user
    g.search_form = SearchForm()

# This is the homepage/categories page!
@app.route('/')
@app.route('/index')
@app.route('/categories')
def index():
    return render_template("index.html")

@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    if request.method == 'GET':
        return render_template('newpost.html')
    elif request.method == 'POST':
        print("user posted!")
        title = request.form.get('title')
        print("Title:", str(title))
        value = request.form.get('value')
        print("Value:", int(value))
        category = request.form.get('category')
        print("Category:", str(category))
        userid = 1
        new_post = model.Listing(seller_id=userid, buyer_id=0, title=title, category=category, cost=value)
        db.session.add(new_post)
        db.session.commit()
        post = Listing.query.filter_by(title=title).first()
        return "All good"


# Once you choose a category, show some transactions from that category
# @app.route('/categories/<category_name>')
# def category(category_name):
#     listings = model.Listing.query.filter_by(category = category_name).limit(20).all()
#
#     numOfListings = len(listings)
#     return render_template("category.html",
#                     category_name = category_name,
#                     numOfListings = numOfListings,
#                     listings = listings)

# Once you choose a category, show some transactions from that category
@app.route('/categories/<category_name>', defaults={'page': 1})
@app.route('/categories/<category_name>/<int:page>')
def category(category_name, page):
    allListings = model.Listing.query.filter_by(category = category_name).all()
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
                           category_name = category_name,
                           numOfListings = count)

# The page for a specific transaction
@app.route('/transactions/<transaction_id>')
def transaction(transaction_id):
    return "You chose the %s transaction!" %(transaction_id)

@app.route('/search', methods=['POST'])
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    return redirect(url_for('search_results', query=g.search_form.search.data))

@app.route('/search_results/<query>')
def search_results(query):
    results = model.Listing.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    return render_template('search_results.html',
                           query=query,
                           results=results)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    return render_template('profile.html', user=current_user, public=False)
