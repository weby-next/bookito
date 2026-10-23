import threading
from django.core.mail import send_mail


def send_async_mail(subject, message, from_email, recipient_list):
    threading.Thread(
        target=send_mail,
        args=(subject, message, from_email, recipient_list),
        kwargs={"fail_silently": False},
    ).start()