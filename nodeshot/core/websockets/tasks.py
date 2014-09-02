from celery import task
from .settings import PUBLIC_PIPE, PRIVATE_PIPE


@task
def send_message(message, pipe='public'):
    """
    writes message to pipe
    """
    if pipe not in ['public', 'private']:
        raise ValueError('pipe argument can be only "public" or "private"')
    else:
        pipe = pipe.upper()

    pipe_path = PUBLIC_PIPE if pipe == 'PUBLIC' else PRIVATE_PIPE

    # create file if it doesn't exist, append contents
    pipeout = open(pipe_path, 'a')

    pipeout.write('%s\n' % message)
    pipeout.close()
