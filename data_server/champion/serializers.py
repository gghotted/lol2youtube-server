from rest_framework import serializers

from champion.models import Champion


class ChampionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Champion
        fields = '__all__'
