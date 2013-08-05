from .OpenWISP import OpenWISP
from .OpenWifiMap import OpenWifiMapMixin


class OpenWISPOpenWifiMap(OpenWifiMapMixin, OpenWISP):
    """
    having real fun.
    """
    REQUIRED_CONFIG_KEYS = [
        'url',
        'openwifimap_url',
    ]