from celery import task


# ------ Asynchronous tasks ------ #


@task
def send_outward_mails(queryset, kwargs):
    """
    Call send method on Outward objects in the background
    """
    for obj in queryset:
        obj.send()
