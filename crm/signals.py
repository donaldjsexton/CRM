from django.db.models.signals import pre_save
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from .models import Client

@receiver(pre_save, sender=Client)
def validate_unique_email(sender, instance, **kwargs):
    if Client.objects.filter(email=instance.email).exclude(pk=instance.pk).exists():
        raise ValidationError(f"A client with email {instance.email} already exists.")

