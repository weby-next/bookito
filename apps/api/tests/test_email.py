from django.core import mail
from django.core.mail import send_mail
from django.test import override_settings


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
)
def test_send_email():
    mail.outbox.clear()

    result = send_mail(
        subject="Bookito Test",
        message="This is a test email.",
        from_email="noreply@bookito.test",
        recipient_list=["customer@example.com"],
        fail_silently=False,
    )

    assert result == 1
    assert len(mail.outbox) == 1

    email = mail.outbox[0]
    assert email.subject == "Bookito Test"
    assert email.to == ["customer@example.com"]
