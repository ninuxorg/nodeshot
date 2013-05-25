"""
useful mixins that can be added to views
"""


class ACLMixin(object):
    """ implements ACL """
    
    def get_queryset(self):
        """
        Returns only objects which are accessible to the current user.
        If user is not authenticated all public objects will be returned.
        
        Model must implement AccessLevelManager!
        """
        return self.queryset.accessible_to(user=self.request.user)