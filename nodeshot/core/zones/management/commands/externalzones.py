from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from nodeshot.core.zones.models import Zone
from importlib import import_module

class Command(BaseCommand):
    args = '<zone_slug zone_slug ...>'
    help = 'Generates json with nodes of an external zone'

    def retrieve_zones(self, *args, **options):
        """ retrieves the zone objects """
        
        # empty Q
        queryset = Q()
        
        # if arguments have been provided
        if len(args) > 0: 
            # loop over args
            for zone_slug in args:
                queryset = queryset | Q(slug=zone_slug)
                # verify existence
                try:
                    # retrieve published external zones
                    zone = Zone.objects.get(slug=zone_slug)
                    
                    # raise exception if zone is not external
                    if not zone.is_external:
                        raise CommandError('Zone "%s" is not an external zone\n\r' % zone_slug)
                    
                    # raise exception if zone is not published
                    if not zone.is_published:
                        raise CommandError('Zone "%s" is not published. Why are you trying to work on an unpublished zone?\n\r' % zone_slug)
                    
                # raise exception if one of the zone looked for doesn't exist
                except Zone.DoesNotExist:
                    raise CommandError('Zone "%s" does not exist\n\r' % zone_slug)
        
        # return published external zones
        return Zone.objects.published().external().select_related().filter(queryset)

    def handle(self, *args, **options):
        self.stdout.write('\r\n')
        
        zones = self.retrieve_zones(*args, **options)
        
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
                instance = interop_class(zone)
                self.stdout.write('Processing zone "%s"\r\n' % zone.slug)
                messages = instance.process()
            except ImproperlyConfigured, e:
                messages = []
                self.stdout.write('Validation error: %s\r\n' % e)
        
            for message in messages:
                self.stdout.write('%s\n\r' % message)
        
        self.stdout.write('\r\n')