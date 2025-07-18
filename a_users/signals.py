from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from allauth.account.models import EmailAddress
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def user_postsave(sender, instance, created, **kwargs):
    user = instance

    # Create user profile if new
    if created:
        Profile.objects.create(user=user)
    else:
        # Try to get primary email
        email_address = EmailAddress.objects.filter(user=user, primary=True).first()

        if email_address:
            if email_address.email != user.email:
                email_address.email = user.email
                email_address.verified = False
                email_address.save()
        else:
            # If EmailAddress doesn't exist, create one
            EmailAddress.objects.create(
                user=user,
                email=user.email,
                primary=True,
                verified=False
            )

@receiver(pre_save, sender=User)
def user_presave(sender, instance, **kwargs):
    if instance.username:
        instance.username = instance.username.lower()
