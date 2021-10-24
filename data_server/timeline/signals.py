from django.db.models.signals import post_save
from django.dispatch import receiver
from event.models import Event

from timeline.models import Timeline


@receiver(post_save, sender=Timeline)
def timeline_post_save(sender, **kwargs):
    timeline = kwargs['instance']

    events = sum(
        (frame.events for frame in timeline.json.dot_data.info.frames),
        []
    )
    for event in events:
        Event.create_by_type(timeline, event)


