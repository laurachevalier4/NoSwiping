from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import re
import os
import hashlib
from babel import dates


def format_datetime(value, format='medium'):
    if format == 'full':
        format = "EEEE, d. MMMM y 'at' HH:mm"
    elif format == 'medium':
        format = "EE dd.MM.y HH:mm"
    return dates.format_datetime(value, format)
    
def format_md5(value):
    return hashlib.md5(value).hexdigest()

def update_or_create(session, model, filters, new_item):
    try:
        exists = session.query(model).filter_by(**filters).one()
        for key, value in new_item.iteritems():
            setattr(exists, key, value)

    except NoResultFound:
        session.add(model(**new_item))

    except MultipleResultsFound, e:
        return 'Multiple results found: %s', e

    return True
