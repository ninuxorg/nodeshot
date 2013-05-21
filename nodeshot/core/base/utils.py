from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.utils.timezone import utc
from datetime import datetime, timedelta


def choicify(dictionary):
    """
    Converts a readable python dictionary into a django model/form
    choice structure (list of tuples) ordered based on the values of each key
    
    :param dictionary: the dictionary to convert
    """
    # get order of the fields
    ordered_fields = sorted(dictionary, key=dictionary.get)
    choices = []
    # loop over each field
    for field in ordered_fields:
        # build tuple (value, i18n_key)
        row = (dictionary[field], _(field.replace('_', ' ')))
        #append tuple to choices
        choices.append(row)
    # return django sorted choices
    return choices


def get_key_by_value(dictionary, search_value):
    """
    searchs a value in a dicionary and returns the key of the first occurrence
    
    :param dictionary: dictionary to search in
    :param search_value: value to search for
    """
    for key, value in dictionary.iteritems():
        if value == search_value:
            return ugettext(key)

# time shortcuts

def now():
    """ returns the current date and time in UTC format (datetime object) """
    return datetime.utcnow().replace(tzinfo=utc)

def now_after(**kwargs):
    """ returns the current date and time plus the time (seconds, minutes, hours, days, years) specified """
    return now() + timedelta(**kwargs)

def after(date, **kwargs):
    """
    returns the result of the calculation of the date param plus the time (seconds, minutes, hours, days, years) specified
    
    :paramm datetime: datetime object to which add more time
    """
    return date + timedelta(**kwargs)