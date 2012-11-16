from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ImproperlyConfigured
from nodeshot.core.zones.models import Zone
from importlib import import_module

class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Generates json with nodes of an external zone'

    def handle(self, *args, **options):
        #for poll_id in args:
        #    try:
        #        poll = Poll.objects.get(pk=int(poll_id))
        #    except Poll.DoesNotExist:
        #        raise CommandError('Poll "%s" does not exist' % poll_id)
        #
        #    poll.opened = False
        #    poll.save()
        
        # retrieve published external zones
        zones = Zone.objects.published().external().select_related()
        
        self.stdout.write('\r\n')
        
        # loop over
        for zone in zones:
            # retrieve interop class if available
            try:
                interop = zone.external.interoperability
            except AttributeError:
                self.stdout.write('Zone %s does not have a config yet\n\r' % zone.name)
            
            # if no interop jump to next zone
            if interop == 'None':
                continue
            
            # else go ahead and import module
            interop_module = import_module(interop)
            # retrieve class name (split and get last piece)
            class_name = interop.split('.')[-1]
            # retrieve class
            interop_class = getattr(interop_module, class_name)
            self.stdout.write('imported module %s\r\n' % interop_module.__file__)
            
            # try running
            try:
                instance = interop_class(zone.external.config)
            except ImproperlyConfigured, e:
                self.stdout.write('Validation error: %s\r\n' % e)
        
        self.stdout.write('\r\n')