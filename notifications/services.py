"""Helpers for sending notifications to users."""

from django.conf import settings
from django.core.mail import send_mail

from .models import Notification


def notify(user, message, link='', email_subject=None):
    """Create an in-app notification and, if requested, also email the user.

    Args:
        user: the user who receives the notification.
        message: the text shown in the notification (and used as the email body).
        link: URL opened when the user clicks the notification.
        email_subject: when given, and the user has an email address,
            the message is also sent by email with this subject.
    """
    Notification.objects.create(user=user, message=message, link=link)
    if email_subject and user.email:
        send_mail(
            subject=email_subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,   # an email failure must not break applying or status updates
        )