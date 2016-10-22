from app import app
from app import model

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
    return "%d listings found for that category" %(len(listings))

# The page for a specific transaction
@app.route('/transactions/<transaction_id>')
def transaction(transaction_id):
    return "You chose the %s transaction!" %(transaction_id)
