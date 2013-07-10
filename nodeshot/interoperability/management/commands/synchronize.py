from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.db.models import Q

from nodeshot.core.layers.models import Layer
from importlib import import_module


class Command(BaseCommand):
    args = '<layer_slug layer_slug ...>'
    help = 'Synchronize external layers with the local database'

    def retrieve_layers(self, *args, **options):
        """
        Retrieve specified layers or all external layers if no layer specified.
        """
        
        # init empty Q object
        queryset = Q()
        
        # if no arguments provided retrieve and return all external layers
        if len(args) < 1:
            self.verbose('no layer specified, will retrieve all layers!')
            return Layer.objects.published().external()
        
        # otherwise loop over args and retrieve each specified layer
        for layer_slug in args:
            queryset = queryset | Q(slug=layer_slug)
            
            # verify existence
            try:
                # retrieve layer
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
    
    def verbose(self, message):
        if self.verbosity == 2:
            self.stdout.write('%s\n\r' % message) 

    def handle(self, *args, **options):
        """ execute synchronize command """
        # store verbosity level in instance attribute for later use
        self.verbosity = int(options.get('verbosity'))
        
        # blank line
        self.stdout.write('\r\n')
        
        # retrieve layers
        layers = self.retrieve_layers(*args, **options)
        
        self.verbose('going to process %d layers...' % len(layers))
        
        # loop over
        for layer in layers:
            # retrieve interop class if available
            try:
                interop = layer.external.interoperability
            except (ObjectDoesNotExist, AttributeError):
                self.stdout.write('External Layer %s does not have an interoperability class specified\n\r' % layer.name)
                continue
            
            # if no interop jump to next layer
            if interop == 'None':
                self.stdout.write('External Layer %s does not have an interoperability class specified\n\r' % layer.name)
                continue
            
            if layer.external.config is None:
                self.stdout.write('Layer %s does not have a config yet\n\r' % layer.name)
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
                instance = interop_class(layer, verbosity=self.verbosity)
                self.stdout.write('Processing layer "%s"\r\n' % layer.slug)
                messages = instance.process()
            except ImproperlyConfigured, e:
                self.stdout.write('Validation error: %s\r\n' % e)
                continue
        
            for message in messages:
                self.stdout.write('%s\n\r' % message)
        
        self.stdout.write('\r\n')