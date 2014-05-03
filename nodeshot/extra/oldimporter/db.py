"""
Django database routers are described here:
https://docs.djangoproject.com/en/dev/topics/db/multi-db/#using-routers
"""


class DefaultRouter(object):
    def db_for_read(self, model, **hints):
        """
        Reads from nodeshot2 db
        """
        if model._meta.app_label != 'oldimporter':
            return 'default'
        return None

    def db_for_write(self, model, **hints):
        """
        Writes to nodeshot2 db
        """
        if model._meta.app_label != 'oldimporter':
            return 'default'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Relations between objects are allowed between nodeshot2 objects only
        """
        if obj1._meta.app_label != 'oldimporter' and \
           obj2._meta.app_label != 'oldimporter':
           return True
        return None

    def allow_syncdb(self, db, model):
        """
        Make sure the old_nodeshot app only appears in the 'old_nodeshot' database
        """
        if db != 'old_nodeshot' and model._meta.app_label != 'oldimporter':
            return True
        return None
    
    allow_migrate = allow_syncdb


class OldNodeshotRouter(object):
    def db_for_read(self, model, **hints):
        """
        Reads old nodeshot models from old_nodeshot db.
        """
        if model._meta.app_label == 'oldimporter':
            return 'old_nodeshot'
        return None

    def db_for_write(self, model, **hints):
        """
        Writes not allowed
        """
        if model._meta.app_label == 'oldimporter':
            return 'old_nodeshot'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Relations between objects are allowed between old_nodeshot objects only
        """
        if obj1._meta.app_label == 'oldimporter' and \
           obj2._meta.app_label == 'oldimporter':
           return True
        return None

    def allow_syncdb(self, db, model):
        """
        Make sure the old_nodeshot app only appears in the 'old_nodeshot' database
        """
        if db != 'old_nodeshot' or model._meta.app_label != 'oldimporter':
            return False
        return True
    
    allow_migrate = allow_syncdb
