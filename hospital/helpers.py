from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from .models import *


def send_confirmation_email(token):
    send_mail(
        subject="Подтвердите email",
        message=f"Перейдите по ссылке для регистрации: {settings.SITE_URL}{reverse('confirm_email', args=[token.token])}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[token.user.email]
    )
