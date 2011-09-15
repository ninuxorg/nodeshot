from settings import SITE

def site(request):
    """
    Adds media-related context variables to the context.

    """
    return {'SITE': SITE}