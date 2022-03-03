from rest_framework.generics import CreateAPIView

from raw_data import serializers


class CrawlableMatchCreateView(CreateAPIView):
    serializer_class = serializers.CrawlableMatchSerializer
