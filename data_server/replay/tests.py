import os
import shutil
import tempfile

from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse_lazy
from event.models import ChampionKill
from match.models import Match

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class KillReplayCreateViewTest(TestCase):
    url = reverse_lazy('replay:kill_create')
    match_id = os.environ['TEST_MATCH_ID']
    replay_path = os.environ['TEST_REPLAY_PATH']

    @classmethod
    def setUpTestData(cls):
        cls.match = Match.objects.create_or_get_from_api(match_id=cls.match_id)
        cls.kill_events = ChampionKill.objects.interested_kills()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_url(self):
        self.assertEqual(self.url, '/replay/')

    def test_normal(self):
        with open(self.replay_path, 'rb') as f:
            data = {
                'file': f,
                'event': self.kill_events.first().pk
            }
            res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 201)

