from datetime import time

from common.models import BaseModel
from django.db import models
from easydict import EasyDict

from event.exceptions import (NotAddableKillSequenceException,
                              NotFoundPrevKillException)
from event.managers import ChampionKillManager


class Event(BaseModel):
    timeline = models.ForeignKey('timeline.Timeline', models.CASCADE)
    type = models.CharField(max_length=64)
    time = models.PositiveIntegerField()
    json_src = models.JSONField()

    class Meta:
        abstract = True

    @staticmethod
    def parse_timeline(data):
        return data.timeline

    @staticmethod
    def parse_type(data):
        return data.type

    @staticmethod
    def parse_time(data):
        return data.timestamp

    @staticmethod
    def parse_json_src(data):
        data = dict(data)
        data.pop('timeline')
        return data

    @staticmethod
    def create_by_type(timeline, data):
        data.timeline = timeline
        event_classes = {
            'CHAMPION_KILL': ChampionKill
        }
        event_cls = event_classes.get(data.type)

        if not event_cls:
            return

        return event_cls.objects.create(**event_cls.parse_json(data))

    @property
    def dot_data(self):
        return EasyDict(self.json_src)

    @property
    def readable_time(self):
        ms = self.time
        s, us = divmod(ms, 1000)
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        return time(
            hour=h,
            minute=m,
            second=s,
            microsecond=us
        )


class NotImplementedEvent(Event):
    pass


class ChampionKill(Event):
    # 오브젝트에 의한 킬이 있으므로, null, blank = True
    killer = models.ForeignKey('match.Participant', models.CASCADE, related_name='kill_events', null=True, blank=True)
    victim = models.ForeignKey('match.Participant', models.CASCADE, related_name='death_events')
    start = models.ForeignKey('self', models.CASCADE, null=True, blank=True, related_name='sequence')
    damage = models.PositiveIntegerField()
    damage_contribution = models.FloatField()

    objects = ChampionKillManager()

    class Meta:
        ordering = ['time']

    @staticmethod
    def parse_killer(data):
        return data.timeline.match.participants.filter(index=data.killerId).first()

    @staticmethod
    def parse_victim(data):
        return data.timeline.match.participants.get(index=data.victimId)

    @staticmethod
    def parse_damage(data):
        return sum(
            damage.magicDamage + damage.physicalDamage + damage.trueDamage
            for damage in data.victimDamageReceived
            if damage.participantId == data.killerId
        )

    @staticmethod
    def parse_damage_contribution(data):
        killer_damage = ChampionKill.parse_damage(data)
        total_damage = sum(
            damage.magicDamage + damage.physicalDamage + damage.trueDamage
            for damage in data.victimDamageReceived
        )
        return killer_damage / total_damage

    def get_prev_kill(self):
        prev_kill = ChampionKill.objects \
                                .filter(
                                    timeline=self.timeline,
                                    killer=self.killer,
                                    time__lte=self.time
                                ).exclude(
                                    id=self.id
                                ).order_by(
                                    '-time'
                                ).first()
        if prev_kill:
            return prev_kill
        else:
            raise NotFoundPrevKillException


    def add_sequence(self, kill):
        if not self.addable(kill):
            raise NotAddableKillSequenceException
        kill.start = self.start
        kill.save()

    def addable(self, kill):
        return all([
            getattr(self, method)(kill)
            for method in dir(self)
            if method.startswith('_addable_check_')
        ])

    def _addable_check_count(self, kill):
        return self.sequence.count() < 5 and kill.sequence.count() == 0

    def _addable_check_killer(self, kill):
        return self.killer == kill.killer

    def _addable_check_victim(self, kill):
        return kill.victim.id not in self.start.sequence.values_list('victim__id', flat=True)

    def _addable_check_time_sequence(self, kill):
        return self.time <= kill.time

    def _addable_check_timeout(self, kill):
        diff_sec = (kill.time - self.time) / 1000
        if self.start.sequence.count() <= 3:
            return diff_sec <= 10
        else:
            return diff_sec <= 30
