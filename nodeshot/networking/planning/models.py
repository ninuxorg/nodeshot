from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.nodes.models import Node
from nodeshot.core.base.choices import PLANNED_STATUS


class PlannedNode(Node):
    date = models.DateTimeField(_('planned for'))
    planning_status = models.SmallIntegerField(_('status'), max_length=1, choices=PLANNED_STATUS, default=0)
    
    class Meta:
        db_table = 'planned_node'
        permissions = (('can_view_planned_nodes', 'Can view planned nodes'),)
