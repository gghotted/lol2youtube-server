import os
from unittest.case import skip

from django.test import TestCase
from match.models import Match
from summoner.models import Summoner
from timeline.models import Timeline

from scripts.crawler import MatchCrawler


class MatchCrawlerTest(TestCase):
    puuid = os.environ['TEST_PUUID']

    @classmethod
    def setUpTestData(cls):
        summoner = Summoner.objects.create(puuid=cls.puuid)
        summoner.update_matches()

    @skip
    def test_100(self):
        MatchCrawler(break_count=100)()
        self.assertGreaterEqual(Match.objects.count(), 100)
        self.assertEqual(Match.objects.count(), Timeline.objects.count())
        self.assertGreaterEqual(Summoner.objects.count(), 1)

    @skip
    def test_1000(self):
        MatchCrawler(break_count=1000)()
        self.assertGreaterEqual(Match.objects.count(), 1000)
        self.assertEqual(Match.objects.count(), Timeline.objects.count())
        self.assertGreaterEqual(Summoner.objects.count(), 1)
