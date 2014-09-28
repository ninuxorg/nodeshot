from __future__ import absolute_import

from nodeshot.interop.sync.synchronizers import OpenWisp
from .citysdk_tourism import CitySdkTourismMixin


class OpenWispCitySdkTourism(CitySdkTourismMixin, OpenWisp):
    """
    OpenWispCitySdkTourism synchronizer class
    Imports data from OpenWISP GeoRSS and then exports the data to the CitySDK database
    """
    SCHEMA = CitySdkTourismMixin.SCHEMA + OpenWisp.SCHEMA

    def convert_format(self, node):
        # determine description or fill some hopefully useful value
        if node.description.strip() == '':
            description = '%s in %s' % (node.name, node.address)
        else:
            description = node.description

        return {
            self.config['citysdk_type'] :{
                "location":{
                   "point":[
                        {
                            "Point":{
                                "posList":"%s %s" % (float(node.point.coords[1]), float(node.point.coords[0])),
                                "srsName":"http://www.opengis.net/def/crs/EPSG/0/4326"
                            },
                            "term": self.config['citysdk_term']
                        }
                    ],
                    "address": {
                        "value":"""BEGIN:VCARD
N:;%s;;;;
ADR;INTL;PARCEL;WORK:;;%s;
END:VCARD""" % (
                            node.name,
                            node.address
                        ),
                        "type": "text/vcard"
                    },
                },
                "label":[
                    {
                        "term": "primary",
                        "value": node.name
                    },
                ],
                "description":[
                    {
                        "value": description,
                        "lang": self.config['citysdk_lang']
                    },
                ],
                "category":[
                    {
                        "id": self.citysdk_category_id
                    }
                ],
                "base": self.citysdk_resource_url,
                "lang": self.config['citysdk_lang'],
                "created": unicode(node.added),
                "author":{
                    "term": "primary",
                    "value": self.layer.organization
                },
                "license":{
                    "term": "primary",
                    "value": "open-data"
                }
            }
        }
