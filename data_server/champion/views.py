from rest_framework.generics import RetrieveAPIView

from champion.models import Champion
from champion.serializers import ChampionSerializer


class MaxPentakillChampionView(RetrieveAPIView):
    serializer_class = ChampionSerializer

    def get_object(self):
        min_count = self.request.GET.get('min_count', 0)
        return Champion.objects.filter(pentakill_count__gte=min_count).order_by('-pentakill_count').first()
