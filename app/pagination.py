from math import ceil
from app import app
from flask import request, url_for

class Pagination(object):

    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and \
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num

def get_listings_for_page(page, PER_PAGE, count, allListings):
    itemsShown = (page - 1) * PER_PAGE
    leftToShow = count - itemsShown

    newListings = []

    if itemsShown < count:
        # If there are still elements to show...
        initialIndex = itemsShown
        if leftToShow >= PER_PAGE:
            # If you can fill a whole page, do it
            finalIndex = itemsShown + NUM_PAGE - 1
            newListings = allListings[initialIndex : finalIndex]
        else:
            # Otherwise, just fill the page with what's left
            newListings = allListings[initialIndex : ]

    return newListings

def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page
