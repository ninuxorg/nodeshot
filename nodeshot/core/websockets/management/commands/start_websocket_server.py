from django.core.management.base import BaseCommand

from nodeshot.core.websockets.server import start as start_server


class Command(BaseCommand):
    help = "Start Tornado WebSocket Server"

    def handle(self, *args, **options):
        """ Go baby go! """
        start_server()
