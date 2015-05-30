from django.conf import settings


DISCOVERY = getattr(settings, 'NODESHOT_OPEN311_DISCOVERY', {
    'changeset':'2014-02-03 14:18',
    'contact':'email or phone number for assistance',
    'key_service':'URL for api_key requests',
    'endpoints':[
        {
            'specification':'http://wiki.open311.org/GeoReport_v2',
            'url':'Public URL of your endpoint',
            'changeset':'2014-02-03 09:01',
            'type':'production',
            'formats':[
                'application/json'
            ]
        },

    ]
})
METADATA = getattr(settings, 'NODESHOT_OPEN311_METADATA', 'true')
TYPE = getattr(settings, 'NODESHOT_OPEN311_TYPE', 'realtime')
STATUS = getattr(settings, 'NODESHOT_OPEN311_STATUS', {
    'potential': 'open',
    'planned': 'open',
    'active': 'closed',
})
