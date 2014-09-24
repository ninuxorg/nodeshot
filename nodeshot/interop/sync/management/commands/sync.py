from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.db.models import Q
from django.utils.module_loading import import_by_path

from nodeshot.core.layers.models import Layer

from optparse import make_option


class Command(BaseCommand):
    args = '<layer_slug layer_slug ...>'
    help = 'Synchronize external layers with the local database'

    option_list = BaseCommand.option_list + (
        make_option(
            '--exclude',
            action='store',
            dest='exclude',
            default=[],
            help='Exclude specific layers from synchronization\n\
                 Supply a comma separated string of layer slugs\n\
                 e.g. --exclude=layer1-slug,layer2-slug,layer3-slug\n\
                 (works only if no layer has been specified)'
        ),
    )

    def retrieve_layers(self, *args, **options):
        """
        Retrieve specified layers or all external layers if no layer specified.
        """

        # init empty Q object
        queryset = Q()

        # if no layer specified
        if len(args) < 1:
            # cache queryset
            all_layers = Layer.objects.published().external()

            # check if there is any layer to exclude
            if options['exclude']:
                # convert comma separated string in python list, ignore spaces
                exclude_list = options['exclude'].replace(' ', '').split(',')
                # retrieve all layers except the ones specified in exclude list
                return all_layers.exclude(slug__in=exclude_list)
            else:
                # nothing to exclude, retrieve all layers
                self.verbose('no layer specified, will retrieve all layers!')
                return all_layers

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
        """ execute sync command """
        # store verbosity level in instance attribute for later use
        self.verbosity = int(options.get('verbosity'))

        # blank line
        self.stdout.write('\r\n')

        # retrieve layers
        layers = self.retrieve_layers(*args, **options)

        if len(layers) < 1:
            self.stdout.write('no layers to process\n\r')
            return
        else:
            self.verbose('going to process %d layers...' % len(layers))

        # loop over
        for layer in layers:
            # retrieve interop class if available
            try:
                synchronizer_path = layer.external.synchronizer_path
            except (ObjectDoesNotExist, AttributeError):
                self.stdout.write('External Layer %s does not have a synchronizer class specified\n\r' % layer.name)
                continue

            # if no synchronizer_path jump to next layer
            if synchronizer_path == 'None':
                self.stdout.write('External Layer %s does not have a synchronizer class specified\n\r' % layer.name)
                continue

            if layer.external.config is None:
                self.stdout.write('Layer %s does not have a config yet\n\r' % layer.name)
                continue

            # retrieve class
            Synchronizer = import_by_path(synchronizer_path)
            self.stdout.write('imported module %s\r\n' % Synchronizer.__name__)

            # try running
            try:
                instance = Synchronizer(layer, verbosity=self.verbosity)
                self.stdout.write('Processing layer "%s"\r\n' % layer.slug)
                messages = instance.process()
            except ImproperlyConfigured, e:
                self.stdout.write('Validation error: %s\r\n' % e)
                continue

            for message in messages:
                self.stdout.write('%s\n\r' % message)

        self.stdout.write('\r\n')
