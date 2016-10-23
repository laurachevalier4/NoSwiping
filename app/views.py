from app import app
from app import model
from flask import render_template, flash, redirect, session, url_for, request, \
    g, jsonify
from flask.ext.login import login_user, logout_user, current_user, \
    login_required

@app.before_request
def before_request():
    g.user = current_user

# This is the homepage/categories page!
@app.route('/')
@app.route('/index')
@app.route('/categories')
def index():
    return render_template("index.html")

@app.route('/newPost', methods=['GET', 'POST'])
def newPost():
    if request.method == 'GET':
        return render_template('newPost.html')

# Once you choose a category, show some transactions from that category
@app.route('/categories/<category_name>')
def category(category_name):
    listings = model.Listing.query.filter_by(category = category_name).limit(20).all()

    numOfListings = len(listings)
    return render_template("category.html",
                    category_name = category_name,
                    numOfListings = numOfListings,
                    listings = listings)

# The page for a specific transaction
@app.route('/transactions/<transaction_id>')
def transaction(transaction_id):
    return "You chose the %s transaction!" %(transaction_id)
