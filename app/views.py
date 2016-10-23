from app import app
from app import model
from flask import render_template

# This is the homepage/categories page!
@app.route('/')
@app.route('/index.html')
@app.route('/categories')
def categories():
    return "There will be categories here. Eventually. Tomorrow for sure..."

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
