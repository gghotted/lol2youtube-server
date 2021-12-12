from champion.models import Ultimate
from event.models import ChampionKill


def run():
    print('#1 start')

    for u in Ultimate.objects.all():
        print(f'#2 {u.id}`s hits init start.(u.hits count: {u.hits.count()})')
        u.hits.clear()
        if u.hits.count() != 0:
            print(f'#3 {u.id}` hits not inited(u.hits count: {u.hits.count()})')
            return

    ChampionKill.objects.exclude(sequence_ultimate_hit_count=0).update(sequence_ultimate_hit_count=0)
    cnt = ChampionKill.objects.exclude(sequence_ultimate_hit_count=0).count()
    print(f'#4 sequence_ultimate_hit_count != ` cnt is {cnt}')
    if cnt != 0:
        return

    qs = ChampionKill.objects.filter(length__in=[3,4,5])
    print(f'#5 {qs.count()} amount ultimate hit update start')
    for obj in qs:
        print(f'#6 {obj} update start.(obj.sequence_ultimate_hit_count: {obj.sequence_ultimate_hit_count})')
        if obj.sequence_ultimate_hit_count != 0:
            return
        
        for sub in obj.sequence.all():
            print(f'#7 {sub} update start.(sub.ultimate_hits.count(): {sub.ultimate_hits.count()}')
            if sub.ultimate_hits.count() != 0:
                return
            sub.set_ultimate_hits()
            print(f'#8 {sub} update finished.(sub.ultimate_hits.count(): {sub.ultimate_hits.count()}')
            obj.sequence_ultimate_hit_count += sub.ultimate_hits.count()

            print(f'#9 {obj} updated subs(obj.sequence_ultimate_hit_count: {obj.sequence_ultimate_hit_count})')
        
        obj.save()
        print(f'#10 {obj}update finished(obj.sequence_ultimate_hit_count: {obj.sequence_ultimate_hit_count})')
