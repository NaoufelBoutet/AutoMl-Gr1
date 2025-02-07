from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import User_project

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_project(sender, instance, created, **kwargs):
    if created:
        User_project.objects.create(user=instance)
