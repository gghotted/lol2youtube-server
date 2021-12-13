from django.db.models.signals import post_save
from django.dispatch import receiver

from event.exceptions import (NotAddableKillSequenceException,
                              NotFoundPrevKillException)
from event.models import ChampionKill


@receiver(post_save, sender=ChampionKill)
def chapion_kill_post_save(sender, **kwargs):
    kill = kwargs['instance']

    if kill.start:
        return

    kill.set_ultimate_hits()

    try:
        prev_kill = kill.get_prev_kill()
        prev_kill.add_sequence(kill)
    except (NotFoundPrevKillException, NotAddableKillSequenceException):
        kill.start = kill
        kill.sequence_ultimate_hit_count = kill.ultimate_hits.count()
        kill.save()
