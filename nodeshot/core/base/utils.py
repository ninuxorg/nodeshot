from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

def choicify(dictionary):
    """ Convert a readable python dictionary into a django model/form choice structure (list of tuples) """
    choices = []
    # loop over dictionary's items, extract key and value for each iteration
    for key, value in dictionary.items():
        # append tuple to "choices" list
        # replace any underscore with a space
        row = (value, _(key.replace('_', ' ')))
        choices.append(row)
    # return django choices
    return choices

def choicify_ordered(dictionary):
    """ Convert a readable python dictionary into a django model/form choice structure (list of tuples) ordered based on the values of each key """
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
    for key, value in dictionary.iteritems():
        if value == search_value:
            return ugettext(key)