from django.db.models.signals import post_save
from django.dispatch import receiver
from pingpong.models import Match


@receiver(post_save, sender=Match)
def my_handler(sender, **kwargs):
    pass