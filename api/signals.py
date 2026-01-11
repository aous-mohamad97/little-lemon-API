from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from djoser.signals import user_registered


@receiver(post_save, sender=User)
def assign_customer_group(sender, instance, created, **kwargs):
    """
    Automatically assign new users to the Customer group when they are created.
    This ensures all new registrations are assigned to the Customer group.
    """
    if created:
        try:
            customer_group, _ = Group.objects.get_or_create(name='Customer')
            # Only add if user doesn't already have other groups (like Manager, Admin, etc.)
            if not instance.groups.exists():
                customer_group.user_set.add(instance)
        except Exception:
            pass  # Silently fail if group doesn't exist yet


@receiver(user_registered)
def assign_customer_group_on_djoser_registration(sender, user, request, **kwargs):
    """
    Assign user to Customer group when registered via djoser.
    """
    try:
        customer_group, _ = Group.objects.get_or_create(name='Customer')
        # Only add if user doesn't already have other groups
        if not user.groups.exists():
            customer_group.user_set.add(user)
    except Exception:
        pass
