import os

from django.conf import settings
from django.test import TestCase
from raw_data.riot_api import MatchListAPI

from match.models import Match


class MatchCreateTest(TestCase):
    puuid = os.environ['TEST_PUUID']

    @classmethod
    def setUpTestData(cls):
        cls.match_list = MatchListAPI(cls.puuid)().json


    def test_create_matches(self):
        matches = Match.objects.creates_or_get_from_api(match_id=self.match_list)
        self.assertEqual(matches.count(), settings.MATCH_LIST_COUNT)

    def test_create_match(self):
        match = Match.objects.create_or_get_from_api(match_id=self.match_list[0])
        self.assertTrue(hasattr(match, 'pk'))
        self.assertEqual(match.participants.count(), settings.MATCH_LIST_COUNT)
