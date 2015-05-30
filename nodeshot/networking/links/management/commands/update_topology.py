from django.core.management.base import BaseCommand

from ...utils import update_topology


class Command(BaseCommand):
    help = 'Update network topology'

    def handle(self, *args, **options):
        update_topology()
