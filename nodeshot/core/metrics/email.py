from djcelery_email.backends import CeleryEmailBackend

from .utils import write_async


class CeleryInfluxDbEmailBackend(CeleryEmailBackend):
    def send_messages(self, email_messages):
        result_tasks = super(CeleryInfluxDbEmailBackend, self).send_messages(email_messages)
        # collect email stats
        write_async(name='emails_sent', values={'value': len(email_messages)})
        return result_tasks
