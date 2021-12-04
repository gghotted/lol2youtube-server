from champion.models import Champion
from match.models import Participant


def run():
    names = set(Participant.objects.all().values_list('champion', flat=True))
    for name in names:
        c, _ = Champion.objects.get_or_create(eng_name=name)
        Participant.objects.filter(champion=name).update(_champion=c)
