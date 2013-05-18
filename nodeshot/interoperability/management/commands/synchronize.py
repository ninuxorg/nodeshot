from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q

from nodeshot.core.layers.models import Layer
from importlib import import_module


class Command(BaseCommand):
    args = '<layer_slug layer_slug ...>'
    help = 'Generates json with nodes of an external layer'

    def retrieve_layers(self, *args, **options):
        """ retrieves the layer objects """
        
        # empty Q
        queryset = Q()
        
        # if arguments have been provided
        if len(args) > 0: 
            # loop over args
            for layer_slug in args:
                queryset = queryset | Q(slug=layer_slug)
                # verify existence
                try:
                    # retrieve published external layers
                    layer = Layer.objects.get(slug=layer_slug)
                    
                    # raise exception if layer is not external
                    if not layer.is_external:
                        raise CommandError('Layer "%s" is not an external layer\n\r' % layer_slug)
                    
                    # raise exception if layer is not published
                    if not layer.is_published:
                        raise CommandError('Layer "%s" is not published. Why are you trying to work on an unpublished layer?\n\r' % layer_slug)
                    
                # raise exception if one of the layer looked for doesn't exist
                except Layer.DoesNotExist:
                    raise CommandError('Layer "%s" does not exist\n\r' % layer_slug)
        
        # return published external layers
        return Layer.objects.published().external().select_related().filter(queryset)

    def handle(self, *args, **options):
        self.stdout.write('\r\n')
        
        layers = self.retrieve_layers(*args, **options)
        
        # loop over
        for layer in layers:
            # retrieve interop class if available
            try:
                interop = layer.external.interoperability
            except AttributeError:
                self.stdout.write('Layer %s does not have a config yet\n\r' % layer.name)
            
            # if no interop jump to next layer
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
                instance = interop_class(layer)
                self.stdout.write('Processing layer "%s"\r\n' % layer.slug)
                messages = instance.process()
            except ImproperlyConfigured, e:
                messages = []
                self.stdout.write('Validation error: %s\r\n' % e)
        
            for message in messages:
                self.stdout.write('%s\n\r' % message)
        
        self.stdout.write('\r\n')