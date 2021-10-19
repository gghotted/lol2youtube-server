import os

from django.test import TestCase

from raw_data.models import JsonData
from raw_data.riot_api import MatchAPI, MatchListAPI, SummonerAPI, TimelineAPI


class RiotApiTest(TestCase):
    def test_summoner_api(self):
        name = os.environ['TEST_SUMMONER_NAME']
        res = SummonerAPI(name=name).get()
        self.assertEqual(res.status_code, 200)

    def test_match_list_api(self):
        puuid = os.environ['TEST_PUUID']
        res = MatchListAPI(puuid).get()
        self.assertEqual(res.status_code, 200)

    def test_match_api(self):
        match_id = os.environ['TEST_MATCH_ID']
        res = MatchAPI(match_id).get()
        self.assertEqual(res.status_code, 200)

    def test_timeline_api(self):
        match_id = os.environ['TEST_MATCH_ID']
        res = TimelineAPI(match_id).get()
        self.assertEqual(res.status_code, 200)


class JsonDataModelTest(TestCase):
    def test_save_summoner(self):
        name = os.environ['TEST_SUMMONER_NAME']
        SummonerAPI(name=name)().save_to_db()

        self.assertEqual(JsonData.objects.summoners().count(), 1)

    def test_save_match(self):
        match_id = os.environ['TEST_MATCH_ID']
        MatchAPI(match_id)().save_to_db()

        self.assertEqual(JsonData.objects.matches().count(), 1)

    def test_save_timeline(self):
        match_id = os.environ['TEST_MATCH_ID']
        TimelineAPI(match_id)().save_to_db()

        self.assertEqual(JsonData.objects.timelines().count(), 1)


class JsonDataModelSignalTest(TestCase):
    def test_post_save_summoner(self):
        name = os.environ['TEST_SUMMONER_NAME']
        SummonerAPI(name=name)().save_to_db()

    def test_post_save_match(self):
        match_id = os.environ['TEST_MATCH_ID']
        MatchAPI(match_id)().save_to_db()

    def test_post_save_timeline(self):
        match_id = os.environ['TEST_MATCH_ID']
        TimelineAPI(match_id)().save_to_db()



