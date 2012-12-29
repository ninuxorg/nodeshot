from django.utils.translation import ugettext_lazy as _

def choicify(dict):
    """ Convert a readable python dictionary into a django model/form choice structure (list of tuples) """
    choices = []
    # loop over dictionary's items, extract key and value for each iteration
    for key, value in dict.items():
        # append tuple to "choices" list
        # replace any underscore with a space
        tuple = (value, _(key.replace('_', ' ')))
        choices.append(tuple)
    # return django choices
    return choices

def choicify_ordered(dict):
    """ Convert a readable python dictionary into a django model/form choice structure (list of tuples) ordered based on the values of each key """
    # get order of the fields
    ordered_fields = sorted(dict, key=dict.get)
    choices = []
    # loop over each field
    for field in ordered_fields:
        # build tuple (value, i18n_key)
        tuple = (dict[field], _(field.replace('_', ' ')))
        #append tuple to choices
        choices.append(tuple)
    # return django sorted choices
    return choices