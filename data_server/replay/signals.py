from django.db.models.signals import pre_delete
from django.dispatch import receiver

from replay.models import LongReplaySource, ReplayFile, ReplaySource


@receiver(pre_delete)
def on_predelete(sender, instance, **kwags):
    if issubclass(sender, (LongReplaySource, ReplayFile, ReplaySource)):
        instance.on_predelete()
