from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CompanyProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_company_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'company':
        CompanyProfile.objects.get_or_create(
            user=instance,
            defaults={'company_name': instance.username},
        )