import logging
logger = logging.getLogger('nodeshot.networking')

from .models import Topology


links_legend = [
    {
        "name": "Link",
        "slug": "link",
        "description": "Active links",
        "fill_color": "#00ff00",
        "stroke_color": "#00ff00",
        "stroke_width": 4,
        "text_color": "#ffffff",
    }
]


def update_topology():
    """
    updates all the topology
    sends logs to the "nodeshot.networking" logger
    """
    for topology in Topology.objects.all():
        try:
            topology.update()
        except Exception as e:
            msg = 'Failed to update {}'.format(topology.__repr__())
            logger.exception(msg)
            print('{0}: {1}\n'
                  'see networking.log for more information\n'.format(msg, e.__class__))
