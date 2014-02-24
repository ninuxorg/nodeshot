"""
Django database routers are described here:
https://docs.djangoproject.com/en/dev/topics/db/multi-db/#using-routers
"""


class DefaultRouter(object):
    def db_for_read(self, model, **hints):
        """
        Reads from nodeshot2 db
        """
        if model._meta.app_label != 'old_nodeshot':
            return 'default'

    def db_for_write(self, model, **hints):
        """
        Writes to nodeshot2 db
        """
        if model._meta.app_label != 'old_nodeshot':
            return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Relations between objects are allowed between nodeshot2 objects only
        """
        if obj1._meta.app_label != 'old_nodeshot' and \
           obj2._meta.app_label != 'old_nodeshot':
           return True
        return None

    def allow_migrate(self, db, model):
        """
        Make sure the old_nodeshot app only appears in the 'old_nodeshot' database
        """
        if db != 'old_nodeshot':
            return True
        return False
    
    allow_syncdb = allow_migrate


class OldNodeshotRouter(object):
    def db_for_read(self, model, **hints):
        """
        Reads old nodeshot models from old_nodeshot db.
        """
        if model._meta.app_label == 'old_nodeshot':
            return 'old_nodeshot'

    def db_for_write(self, model, **hints):
        """
        Writes not allowed
        """
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Relations between objects are allowed between old_nodeshot objects only
        """
        if obj1._meta.app_label == 'old_nodeshot' and \
           obj2._meta.app_label == 'old_nodeshot':
           return True
        return None

    def allow_migrate(self, db, model):
        """
        Make sure the old_nodeshot app only appears in the 'old_nodeshot' database
        """
        if db == 'old_nodeshot':
            return model._meta.app_label == 'old_nodeshot'
        elif model._meta.app_label == 'old_nodeshot':
            return False
        return None
    
    allow_syncdb = allow_migrate