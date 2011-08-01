from django.utils.hashcompat import sha_constructor
from django.conf import settings as djsettings
from random import choice
from binascii import hexlify, unhexlify
import settings


def question():
    n1, n2 = choice(settings.NUMBERS), choice(settings.NUMBERS)

    if n2 > n1:
        # avoid negative answers
        n1, n2 = n2, n1

    return "%s %s %s" % (n1, choice(settings.OPERATORS), n2)
    
def encode(question):
    """
    Given a mathematical question, eg '1 - 2 + 3', the question is hashed
    with the ``SECRET_KEY`` and the hex version of the question is appended.
    To the end user it looks like an extra long hex string, but it cryptographically ensures
    against any tampering. 
    """
    return sha_constructor(djsettings.SECRET_KEY + question).hexdigest() + hexlify(question)
    
def decode(answer):
    """
    Returns the SHA1 answer key and the math question text.
    If the answer key passes, the question text is evaluated and compared to the user's answer.
    """
    return answer[:40], unhexlify(answer[40:])
