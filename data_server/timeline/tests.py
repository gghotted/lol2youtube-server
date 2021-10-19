import os

from django.conf import settings
from django.test import TestCase
from match.models import Match
from raw_data.riot_api import MatchListAPI

from timeline.models import Timeline


class TimelineCreateTest(TestCase):
    puuid = os.environ['TEST_PUUID']

    @classmethod
    def setUpTestData(cls):
        cls.match_list = MatchListAPI(cls.puuid)().json

    def test_create_timelines(self):
        Match.objects.creates_or_get_from_api(match_id=self.match_list)
        self.assertEqual(Timeline.objects.count(), settings.MATCH_LIST_COUNT)

    def test_create_timeline(self):
        Match.objects.create_or_get_from_api(match_id=self.match_list[0])
        timeline = Timeline.objects.first()
        self.assertTrue(hasattr(timeline, 'pk'))
