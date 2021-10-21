import os

from django.conf import settings
from django.test import TestCase
from raw_data.riot_api import MatchListAPI

from match.models import Match, Participant


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


class ParticipantCreateTest(TestCase):
    match_id = os.environ['TEST_MATCH_ID']

    @classmethod
    def setUpTestData(cls):
        cls.match = Match.objects.create_or_get_from_api(match_id=cls.match_id)

    def test_create_participant(self):
        data = self.match.json.dot_data.info.participants[0]
        participant = Participant.objects.create(
            match=self.match,
            **Participant.parse_json(data)
        )

        self.assertEqual(participant.champion, data.championName)
        self.assertEqual(participant.index, data.participantId)

        self.assertEqual(participant.summoner.name, data.summonerName)
        self.assertEqual(participant.summoner.puuid, data.puuid)


