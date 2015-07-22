from celery import task


@task
def create_related_object(model, kwargs):
    """
    create object with specified kwargs in background
    """
    model.objects.create(**kwargs)
