import os
from datetime import time

from django.test import TestCase
from easydict import EasyDict
from match.models import Match, Participant
from timeline.models import Timeline

from event.models import ChampionKill, Event, NotImplementedEvent


class EventCreateTest(TestCase):
    match_id = os.environ['TEST_MATCH_ID']

    @classmethod
    def setUpTestData(cls):
        cls.match = Match.objects.create_or_get_from_api(match_id=cls.match_id)
        cls.timeline = Timeline.objects.create_or_get_from_api(match_id=cls.match_id)
        cls.events = sum(
            (frame.events for frame in cls.timeline.json.dot_data.info.frames),
            []
        )

    def test_not_implemented_event(self):
        event = EasyDict(type='random', dummy_data='dummy', timestamp=0)
        Event.create_by_type(
            self.timeline,
            event
        )
        self.assertEqual(NotImplementedEvent.objects.count(), 1)

    def test_implemented_event(self):
        kill_events = list(filter(
            lambda e: e.type == 'CHAMPION_KILL',
            self.events
        ))
        Event.create_by_type(
            self.timeline,
            kill_events[0]
        )
        self.assertEqual(ChampionKill.objects.count(), 1)


class ChampionKillCreateTest(TestCase):
    match_id = os.environ['TEST_PENTAKILL_MATCH_ID']

    @classmethod
    def setUpTestData(cls):
        cls.match = Match.objects.create_or_get_from_api(match_id=cls.match_id)
        cls.timeline = Timeline.objects.create_or_get_from_api(match_id=cls.match_id)
        cls.events = sum(
            (frame.events for frame in cls.timeline.json.dot_data.info.frames),
            []
        )
        cls.kill_events = list(filter(
            lambda e: e.type == 'CHAMPION_KILL',
            cls.events
        ))

    def test_single_kill(self):
        kill = Event.create_by_type(
            self.timeline,
            self.kill_events[0]
        )
        kill = ChampionKill.objects.get(id=kill.id)

        self.assertTrue(isinstance(kill.killer, Participant))
        self.assertTrue(isinstance(kill.victim, Participant))
        self.assertEqual(kill.start, kill)
        self.assertGreater(kill.damage, 0)
        self.assertGreater(kill.damage_contribution, 0)

        self.assertEqual(kill.length, 1)
        self.assertEqual(kill.avg_interval, 0)
        self.assertEqual(kill.avg_damage, kill.damage)

    def test_penta_kill(self):
        for kill_event in self.kill_events:
            Event.create_by_type(
                self.timeline,
                kill_event
            )

        pentakills = ChampionKill.objects.root_kills(length=5)
        self.assertEqual(pentakills.count(), 1)

        pentakill = pentakills.first()
        self.assertEqual(pentakill.sequence.count(), 5)
        self.assertEqual(
            pentakill.avg_interval,
            (pentakill.sequence.last().time - pentakill.sequence.first().time) / pentakill.length
        )
        self.assertEqual(
            pentakill.avg_damage,
            sum(
                k.damage
                for k in pentakill.sequence.all()
            ) / pentakill.length
        )

    def test_sequence(self):
        kill1 = self.kill_events[0]
        kill1 = Event.create_by_type(self.timeline, kill1)

        # after 9 sec
        kill2 = EasyDict(self.kill_events[1])
        kill2.timestamp = kill1.time + (9 * 1000)
        kill2.killerId = kill1.killer.index

        victims = set(range(1, 11))
        victims.remove(kill1.victim.index)
        kill2.victim = list(victims)[0]
        kill2 = Event.create_by_type(self.timeline, kill2)

        kill1 = ChampionKill.objects.get(id=kill1.id)
        kill2 = ChampionKill.objects.get(id=kill2.id)

        self.assertEqual(kill1.sequence.count(), 2)
        self.assertEqual(kill2.sequence.count(), 0)
        self.assertEqual(kill1.sequence.last(), kill2)

        self.assertEqual(kill1.avg_damage, (kill1.damage + kill2.damage) / 2)
        self.assertEqual(kill2.avg_damage, None)

        self.assertEqual(kill1.avg_damage_contribution, (kill1.damage_contribution + kill2.damage_contribution) / 2)
        self.assertEqual(kill2.avg_damage_contribution, None)

        self.assertEqual(kill1.avg_interval, (kill2.time - kill1.time) / 2)
        self.assertEqual(kill2.avg_interval, None)

        self.assertEqual(kill1.start, kill1)
        self.assertEqual(kill2.start, kill1)






