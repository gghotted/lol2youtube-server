from datetime import time

from champion.models import Champion, Ultimate
from common.models import BaseModel
from django.db import models
from easydict import EasyDict

from event.exceptions import (NotAddableKillSequenceException,
                              NotFoundPrevKillException)
from event.managers import ChampionKillManager, InterestScoreManager


class InterestScore(BaseModel):
    '''
    real_value가 낮을수록 낮은 점수
    '''
    low_is_good = False

    '''
    스코어에 해당하는 타켓의 모델과 필드
    '''
    target_model = None
    target_field = ''
    score_field_postfix = '_score'

    '''
    normalize에 사용할 쿼리셋 필터
    '''
    normalize_qs_filters = dict()

    VALUE_CHOICES = [(i, i) for i in range(1, 11)]
    value = models.IntegerField(choices=VALUE_CHOICES)
    lte_boundary = models.FloatField()
    gt_boundary = models.FloatField()

    objects = InterestScoreManager()

    class Meta:
        abstract = True

    @classmethod
    def evaluate(cls, real_value):
        return cls.objects.get(lte_boundary__lte=real_value, gt_boundary__gt=real_value)


class DurationScore(InterestScore):
    low_is_good = True
    target_model = 'event.ChampionKill'
    target_field = 'duration'
    normalize_qs_filters = {
        'length__in': [2, 3, 4, 5],
    }


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
    timeline = models.ForeignKey('timeline.Timeline', models.CASCADE, related_name='championkills')
    # 오브젝트에 의한 킬이 있으므로, null, blank = True
    killer = models.ForeignKey('match.Participant', models.CASCADE, related_name='kill_events', null=True, blank=True)
    victim = models.ForeignKey('match.Participant', models.CASCADE, related_name='death_events')
    start = models.ForeignKey('self', models.CASCADE, null=True, blank=True, related_name='sequence')
    damage = models.PositiveIntegerField()
    damage_contribution = models.FloatField()
    bounty = models.PositiveIntegerField()
    length = models.PositiveIntegerField(default=1)

    '''
    sequence에서 first와 last의 시간 차
    '''
    duration = models.FloatField(default=float('inf'))

    '''
    duration의 1~10점 사이의 점수
    duration값이 작을 수록 interest함 -> 작을 수록 높은 점수
    '''
    duration_score = models.ForeignKey('event.DurationScore', models.DO_NOTHING, null=True)

    ultimate_hits = models.ManyToManyField('champion.Ultimate', related_name='hits')
    sequence_ultimate_hit_count = models.PositiveBigIntegerField(default=0)

    objects = ChampionKillManager()

    class Meta:
        ordering = ['id']

    def sum_field_sequence(self, field):
        return sum(
            getattr(kill, field)
            for kill in self.sequence.all()
        )

    @property
    def total_damage(self):
        return self.sum_field_sequence('damage')

    @property
    def total_damage_contribution(self):
        return self.sum_field_sequence('damage_contribution') / self.length

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

    @staticmethod
    def parse_bounty(data):
        return data.bounty

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

    def set_ultimate_hits(self):
        for received in self.json_src['victimDamageReceived']:
            slot = received.get('spellSlot')
            name = received.get('name')
            if slot == 3 and name in Ultimate.INTEREST_ULTIMATE_CHAMPION_NAME:
                champion, _ = Champion.objects.get_or_create(eng_name=name)
                ultimate, _ = Ultimate.objects.get_or_create(champion=champion)
                self.ultimate_hits.add(ultimate)

    def add_sequence(self, kill):
        if not self.addable(kill):
            raise NotAddableKillSequenceException
        self._add_sequence(kill)

    def _add_sequence(self, kill):
        self._set_length(kill)
        self._set_duration(kill)
        self._set_ultimate_hit_count(kill)
        self._set_start(kill)
        self.start.save()
        kill.save()

    def _set_length(self, kill):
        self.start.length += 1
        kill.length = 0

    def _set_duration(self, kill):
        if self.start.length < 2:
            return
        self.start.duration = (kill.time - self.start.time) / self.start.length
        self.start.duration_score = DurationScore.evaluate(self.start.duration)

    def _set_ultimate_hit_count(self, kill):
        self.start.sequence_ultimate_hit_count += kill.ultimate_hits.count()

    def _set_start(self, kill):
        kill.start = self.start

    def addable(self, kill):
        return all([
            getattr(self, method)(kill)
            for method in dir(self)
            if method.startswith('_addable_check_')
        ])

    def _addable_check_count(self, kill):
        return self.length < 5 and kill.length == 1

    def _addable_check_killer(self, kill):
        return (self.killer == kill.killer) and (self.killer is not None)

    def _addable_check_victim(self, kill):
        return kill.victim.id not in self.start.sequence.values_list('victim__id', flat=True)

    def _addable_check_time_sequence(self, kill):
        return self.time <= kill.time

    def _addable_check_timeout(self, kill):
        diff_sec = (kill.time - self.time) / 1000
        if self.start.length <= 3:
            return diff_sec <= 10
        else:
            return diff_sec <= 30
