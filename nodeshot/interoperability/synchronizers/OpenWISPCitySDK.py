from .OpenWISP import OpenWISP
from .CitySDKMixin import CitySDKMixin


class OpenWISPCitySDK(CitySDKMixin, OpenWISP):
    """
    OpenWISPCitySDK interoperability class
    Imports data from OpenWISP GeoRSS and then exports the data to the CitySDK database
    """
    
    def convert_format(self, node):
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
                        "value": node.description,
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