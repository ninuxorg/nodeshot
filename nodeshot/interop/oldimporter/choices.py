from django.utils.translation import ugettext_lazy as _
from .settings import settings


ROUTING_PROTOCOLS = (
    ('aodv','AODV'),
    ('batman','B.A.T.M.A.N.'),
    ('dsdv','DSDV'),
    ('dsr','DSR'),
    ('hsls','HSLS'),
    ('iwmp','IWMP'),
    ('olsr','OLSR'),
    ('oorp','OORP'),
    ('ospf','OSPF'),
    ('tora','TORA'),
)

DEFAULT_ROUTING_PROTOCOL = 'olsr'
ACTIVATION_DAYS = 7

SITE = {
    'name': 'Nodeshot',
    'domain': 'http://test.test.com'
}

NODE_STATUS = (
    ('p', _('potential')),
    ('a', _('active')),
    ('h', _('hotspot')),
    ('ah', _('active & hotspot')),
    ('u', _('unconfirmed')), # nodes that have not been confirmed via email yet
)

INTERFACE_TYPE = (
    ('wifi', _('wifi')),
    ('eth', _('ethernet')),
    ('vpn', _('vpn')),
    ('batman', _('batman')),
    ('bridge', _('bridge')),
    ('vwifi', _('virtual-wifi')),
    ('veth', _('virtual-ethernet'))
)

INTERFACE_STATUS = (
    ('r', _('reachable')),
    ('u', _('unreachable'))
)

WIRELESS_MODE = (
    ('sta', _('station')),
    ('ap', _('access point')),
    ('adhoc', _('adhoc')),
)

WIRELESS_POLARITY = (
    ('h', _('horizontal')),
    ('v', _('vertical')),
    ('c', _('circular')),
    ('a', _('auto')),
)

WIRELESS_CHANNEL = (
    ('2412', '2.4Ghz Ch  1 (2412 Mhz)'),
    ('2417', '2.4Ghz Ch  2 (2417 Mhz)'),
    ('2422', '2.4Ghz Ch  3 (2422 Mhz)'),
    ('2427', '2.4Ghz Ch  4 (2427 Mhz)'),
    ('2427', '2.4Ghz Ch  5 (2432 Mhz)'),
    ('2437', '2.4Ghz Ch  6 (2437 Mhz)'),
    ('2442', '2.4Ghz Ch  7 (2442 Mhz)'),
    ('2447', '2.4Ghz Ch  8 (2447 Mhz)'),
    ('2452', '2.4Ghz Ch  9 (2452 Mhz)'),
    ('2457', '2.4Ghz Ch  10 (2457 Mhz)'),
    ('2462', '2.4Ghz Ch  11 (2462 Mhz)'),
    ('2467', '2.4Ghz Ch  12 (2467 Mhz)'),
    ('2472', '2.4Ghz Ch  13 (2472 Mhz)'),
    ('2484', '2.4Ghz Ch  14 (2484 Mhz)'),
    ('4915', '5Ghz Ch 183 (4915 Mhz)'),
    ('4920', '5Ghz Ch 184 (4920 Mhz)'),
    ('4925', '5Ghz Ch 185 (4925 Mhz)'),
    ('4935', '5Ghz Ch 187 (4935 Mhz)'),
    ('4940', '5Ghz Ch 188 (4940 Mhz)'),
    ('4945', '5Ghz Ch 189 (4945 Mhz)'),
    ('4960', '5Ghz Ch 192 (4960 Mhz)'),
    ('4980', '5Ghz Ch 196 (4980 Mhz)'),
    ('5035', '5Ghz Ch 7 (5035 Mhz)'),
    ('5040', '5Ghz Ch 8 (5040 Mhz)'),
    ('5045', '5Ghz Ch 9 (5045 Mhz)'),
    ('5055', '5Ghz Ch 11 (5055 Mhz)'),
    ('5060', '5Ghz Ch 12 (5060 Mhz)'),
    ('5080', '5Ghz Ch 16 (5080 Mhz)'),
    ('5170', '5Ghz Ch 34 (5170 Mhz)'),
    ('5180', '5Ghz Ch 36 (5180 Mhz)'),
    ('5190', '5Ghz Ch 38 (5190 Mhz)'),
    ('5200', '5Ghz Ch 40 (5200 Mhz)'),
    ('5210', '5Ghz Ch 42 (5210 Mhz)'),
    ('5220', '5Ghz Ch 44 (5220 Mhz)'),
    ('5230', '5Ghz Ch 46 (5230 Mhz)'),
    ('5240', '5Ghz Ch 48 (5240 Mhz)'),
    ('5260', '5Ghz Ch 52 (5260 Mhz)'),
    ('5280', '5Ghz Ch 56 (5280 Mhz)'),
    ('5300', '5Ghz Ch 60 (5300 Mhz)'),
    ('5320', '5Ghz Ch 64 (5320 Mhz)'),
    ('5500', '5Ghz Ch 100 (5500 Mhz)'),
    ('5520', '5Ghz Ch 104 (5520 Mhz)'),
    ('5540', '5Ghz Ch 108 (5540 Mhz)'),
    ('5560', '5Ghz Ch 112 (5560 Mhz)'),
    ('5580', '5Ghz Ch 116 (5580 Mhz)'),
    ('5600', '5Ghz Ch 120 (5600 Mhz)'),
    ('5620', '5Ghz Ch 124 (5620 Mhz)'),
    ('5640', '5Ghz Ch 128 (5640 Mhz)'),
    ('5660', '5Ghz Ch 132 (5660 Mhz)'),
    ('5680', '5Ghz Ch 136 (5680 Mhz)'),
    ('5700', '5Ghz Ch 140 (5700 Mhz)'),
    ('5745', '5Ghz Ch 149 (5745 Mhz)'),
    ('5765', '5Ghz Ch 153 (5765 Mhz)'),
    ('5785', '5Ghz Ch 157 (5785 Mhz)'),
    ('5805', '5Ghz Ch 161 (5805 Mhz)'),
    ('5825', '5Ghz Ch 165 (5825 Mhz)')
)
