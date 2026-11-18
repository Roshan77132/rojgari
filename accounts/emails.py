"""Emails sent by the accounts app."""

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def send_verification_email(request, user):
    """Email the user a one-time link to verify their email address.

    The link contains the user id (base64) and a signed token, so it cannot be
    guessed and stops working once the account is verified or the token expires.
    """
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    link = request.build_absolute_uri(
        reverse('accounts:verify_email', args=[uid, token])
    )
    send_mail(
        subject='RojGari: verify your email',
        message=(
            f"Hello {user.username},\n\n"
            f"Click the link below to verify your email:\n{link}\n\n"
            "If you did not create this account, please ignore this email."
        ),
        from_email=None,   # None = use DEFAULT_FROM_EMAIL from settings
        recipient_list=[user.email],
    )