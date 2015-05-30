"""
Dependencies:
    * nodeshot.core.nodes
    * nodeshot.networking.net
    * django_hstore
"""

from nodeshot.core.base.utils import check_dependencies

check_dependencies(
    dependencies=[
        'nodeshot.core.nodes',
        'nodeshot.networking.net',
        'django_hstore'
    ],
    module='nodeshot.networking.connector'
)


from .device_connector import DeviceConnector


__all__ = ['DeviceConnector']