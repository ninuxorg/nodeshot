from django.dispatch import Signal


user_logged_in = Signal(providing_args=["request", "user"])
password_changed = Signal(providing_args=["user"])

email_confirmed = Signal(providing_args=["email_address"])
email_confirmation_sent = Signal(providing_args=["confirmation"])
