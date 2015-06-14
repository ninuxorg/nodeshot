class LinkException(Exception):
    pass


class LinkDataNotFound(LinkException):
    """
    Ip addresses or mac addresses not present in the database
    """
    pass


class LinkNotFound(LinkException):
    """
    Ip addresses or mac addresses are present but Link does not exist
    """
    def __init__(self, *args, **kwargs):
        self.interface_a = kwargs.pop('interface_a')
        self.interface_b = kwargs.pop('interface_b')
        self.topology = kwargs.pop('topology')
