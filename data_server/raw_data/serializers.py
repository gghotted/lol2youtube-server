from rest_framework import serializers

from raw_data.models import CrawlableMatch


class CrawlableMatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrawlableMatch
        fields = ('id', )
