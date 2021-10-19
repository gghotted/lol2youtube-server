from django.db.models.signals import post_save
from django.dispatch import receiver
from summoner.models import Summoner
from timeline.models import Timeline

from match.models import Match


@receiver(post_save, sender=Match)
def match_post_save(sender, **kwargs):
    match = kwargs['instance']
    # annotate 속성을 가져오기 위함
    match = Match.objects.get(id=match.id)

    participants = match.json.dot_data.metadata.participants

    Summoner.objects.bulk_create(
        [Summoner(puuid=puuid) for puuid in participants], ignore_conflicts=True
    )
    match.participants.add(
        *Summoner.objects.filter(puuid__in=participants)
    )

    Timeline.objects.create_or_get_from_api(match_id=match.id)
    print_log(match)


def print_log(match):
    s = '{game_creation}, {pentakill}/{quadrakill}/{triplekill}/{total}/{is_interested}, {id}({queue_id})'.format(
        game_creation=match.game_creation,
        pentakill=Match.objects.filter(has_pentakill=True).count(),
        quadrakill=Match.objects.filter(has_quadrakill=True).count(),
        triplekill=Match.objects.filter(has_triplekill=True).count(),
        total=Match.objects.count(),
        is_interested=match.is_interested,
        id=match.id,
        queue_id=match.queue_id,
    )
    print(s)

