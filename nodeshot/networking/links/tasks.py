from celery import task

from .utils import update_topology as update_topology_util


@task
def update_topology():
    """
    celery task wrapper for nodeshot.networking.utils.update_topology
    """
    update_topology_util()
