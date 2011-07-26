import math
from django.contrib.auth.models import User
from django.template.loader import render_to_string

def distance(origin, destination):
    'Haversine formula'
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371 # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d

def signal_to_bar(signal):
    if signal < 0:
        return min(100, max(0, int( 100-( (-signal -50) * 10/4 ) ) ) ) 
    else:
        return 0
    
def notify_admins(node, subject_template, body_template, context, skip=False):
    ''' todo: comment this '''
    admins = User.objects.filter(is_staff=True, userprofile__receive_notifications=True).exclude(email='').select_related().order_by('pk')
    if(len(admins)>0):
        # parse subject (which is the same for every admin)
        subject = render_to_string(subject_template,context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        # loop over admins
        for admin in admins:
            # if skip is True and admin is one of the owners do not break his balls again please
            if skip and admin.email == node.email or admin.email == node.email2 or admin.email == node.email3:
                continue
            # include user information in context
            context['admin'] = admin
            # parse message
            message = render_to_string(body_template,context)
            # send email
            admin.email_user(subject, message)