from celery import task


# ------ Asynchronous tasks ------ #


@task
def send_outward_mails(queryset):
    """
    Call send method on Outward objects in the background
    """
    for obj in queryset:
        obj.send()
