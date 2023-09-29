from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import User, UserProfile


# signal
@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    if created:
        # Create the userprofile if not exist
        UserProfile.objects.create(user=instance)
    else:
        try:
            # if userprofile exist
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except:
            # Create the userprofile if not exist
            UserProfile.objects.create(user=instance)
