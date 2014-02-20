import os
from django.conf import settings
from celery import task


@task
def send_message(message, pipe='public'):
    """
    writes message to pipe
    """
    if pipe not in ['public', 'private']:
        raise ArgumentError('pipe argument can be only "public" or "private"')
    else:
        pipe = pipe.upper()
    
    pipe_path = settings.NODESHOT['WEBSOCKETS']['%s_PIPE' % pipe]
    
    # create file if it doesn't exist, append contents
    pipeout = open(pipe_path, 'a')
    
    pipeout.write('%s\n' % message)
    pipeout.close()