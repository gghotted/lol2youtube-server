import os
import time
from datetime import datetime, timedelta

from django.conf import settings
from django.test import TestCase
from match.models import Match

from summoner.models import Summoner


class SummonerCreateTest(TestCase):
    puuid = os.environ['TEST_PUUID']

    def test_summoner_create(self):
        Summoner.objects.create_or_get_from_api(
            puuid=self.puuid,
        )
        self.assertEqual(Summoner.objects.count(), 1)


class SummonerUpdateMatchTest(TestCase):
    puuid = os.environ['TEST_PUUID']

    @classmethod
    def setUpTestData(cls):
        cls.summoner = Summoner.objects.create_or_get_from_api(
            puuid=cls.puuid,
        )

    def test_summoner_update(self):
        self.summoner.update_matches()
        self.assertGreater(Summoner.objects.count(), 1)
        self.assertEqual(Match.objects.count(), settings.MATCH_LIST_COUNT)
        self.assertLessEqual(self.summoner.match_updated_at, datetime.now())


class SummonerGetToUpdateTest(TestCase):
    puuid = os.environ['TEST_PUUID']
    min_update_time = settings.SUMMONER_MIN_UPDATE_TIME

    @classmethod
    def setUpTestData(cls):
        summoner = Summoner.objects.create(puuid=cls.puuid)
        summoner.update_matches()

    def test_normal(self):
        recent_match = Match.objects.order_by('-game_creation').first()
        summoner = Summoner.objects.get_to_update()
        self.assertTrue(recent_match.participants.filter(puuid=summoner.puuid).exists())

    def test_filter_updated_summoners(self):
        before_count = Summoner.objects.order_by_update_priority().count()

        summoner = Summoner.objects.get_to_update()
        summoner.match_updated_at = datetime.now()
        summoner.save()
        after_count = Summoner.objects.order_by_update_priority().count()

        self.assertEqual(before_count - 1, after_count)

    def test_priority_ordering(self):
        summoners = list(Summoner.objects.order_by_update_priority())
        sorted_by_game_creation = sorted(
            summoners,
            key=lambda s: s.matches.order_by('-game_creation').first().game_creation,
            reverse=True
        )
        self.assertEqual(summoners, sorted_by_game_creation)

        for summoners in self._group_by_match(summoners):
            sorted_by_match_updated_at = sorted(
                summoners,
                key=lambda s: s.match_updated_at
            )
            self.assertEqual(summoners, sorted_by_match_updated_at)

    def test_min_update_time_out(self):
        before_count = Summoner.objects.order_by_update_priority().count()

        update_time = datetime.now() - (self.min_update_time - timedelta(seconds=1))
        summoner = Summoner.objects.get_to_update()
        summoner.match_updated_at = update_time
        summoner.save()
        after_update_count = Summoner.objects.order_by_update_priority().count()
        self.assertEqual(before_count - 1, after_update_count)

        time.sleep(2)
        after_timeout_count = Summoner.objects.order_by_update_priority().count()
        self.assertEqual(before_count, after_timeout_count)

    def _group_by_match(self, summoners):
        group = []

        for summoner in summoners:
            if len(group) == 0:
                group.append(summoner)
                continue

            if summoner.matches.order_by('-game_creation').first() == \
               group[-1].matches.order_by('-game_creation').first():
                group.append(summoner)
            else:
                yield group
                group = []






