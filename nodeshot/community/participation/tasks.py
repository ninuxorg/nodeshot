from celery import task


# ------ Asynchronous tasks ------ #


@task
def create_related_object(model, kwargs):
    """
    create object with specified kwargs in background
    """
    model.objects.create(**kwargs)