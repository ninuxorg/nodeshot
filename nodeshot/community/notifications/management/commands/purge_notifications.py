from django.core.management.base import BaseCommand

from nodeshot.community.notifications.models import Notification
from nodeshot.core.base.utils import ago

from ...settings import settings, DELETE_OLD


class Command(BaseCommand):
    help = "Delete notifications older than DELETE_OLD"

    def retrieve_old_notifications(self):
        """
        Retrieve notifications older than X days, where X is specified in settings
        """

        date = ago(days=DELETE_OLD)

        return Notification.objects.filter(added__lte=date)

    def output(self, message):
        self.stdout.write('%s\n\r' % message)

    def handle(self, *args, **options):
        """ Purge notifications """
        # retrieve layers
        notifications = self.retrieve_old_notifications()
        count = len(notifications)

        if count > 0:
            self.output('found %d notifications to purge...' % count)
            notifications.delete()
            self.output('%d notifications deleted successfully.' % count)
        else:
            self.output('there are no old notifications to purge')
