from celery import task
from django.utils.module_loading import import_by_path
from django.core import management


@task
def synchronize_external_layers(*args, **kwargs):
    """
    runs "python manage.py synchronize"
    """
    management.call_command('sync', *args, **kwargs)


# ------ Asynchronous tasks ------ #


@task
def push_changes_to_external_layers(node, external_layer, operation):
    """
    Sync other applications through their APIs by performing updates, adds or deletes.
    This method is designed to be performed asynchronously, avoiding blocking the user
    when he changes data on the local DB.

    :param node: the node which should be updated on the external layer.
    :type node: Node model instance
    :param operation: the operation to perform (add, change, delete)
    :type operation: string
    """
    # putting the model inside prevents circular imports
    # subsequent imports go and look into sys.modules before reimporting the module again
    # so performance is not affected
    from nodeshot.core.nodes.models import Node
    # get node because for some reason the node instance object is not passed entirely,
    # pheraphs because objects are serialized by celery or transport/queuing mechanism
    if not isinstance(node, basestring):
        node = Node.objects.get(pk=node.pk)
    # import synchronizer
    Synchronizer = import_by_path(external_layer.synchronizer_path)
    # create instance
    instance = Synchronizer(external_layer.layer)
    # call method only if supported
    if hasattr(instance, operation):
        getattr(instance, operation)(node)
