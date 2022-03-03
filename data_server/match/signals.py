from django.db.models.signals import post_save
from django.dispatch import receiver
from timeline.models import Timeline

from match.models import Match, Participant


@receiver(post_save, sender=Match)
def match_post_save(sender, **kwargs):
    match = kwargs['instance']
    # annotate 속성을 가져오기 위함
    match = Match.objects.get(id=match.id)

    # 참가자 생성 및 연결
    participants = match.json.dot_data.info.participants
    for idx, dot_data in enumerate(participants):
        Participant.objects.create(match=match, **Participant.parse_json(dot_data))

    # 타임라인 생성
    if match.has_pentakill:
        Timeline.objects.create_or_get_from_api(match_id=match.id)
        print_log(match)


def print_log(match):
    s = '{game_creation}, {pentakill}/{quadrakill}/{triplekill}/{total}, {id}({queue_id})'.format(
        game_creation=match.game_creation,
        pentakill=Match.objects.filter(has_pentakill=True).count(),
        quadrakill=Match.objects.filter(has_quadrakill=True).count(),
        triplekill=Match.objects.filter(has_triplekill=True).count(),
        total=Match.objects.count(),
        id=match.id,
        queue_id=match.queue_id,
    )
    print(s)

