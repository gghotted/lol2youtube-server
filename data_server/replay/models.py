from pathlib import Path

from common.models import BaseModel
from django.db import models
from youtube.models import UploadInfo

from replay.managers import ReplaySourceManager


class ReplayBlackList(BaseModel):
    match = models.ForeignKey('match.Match', on_delete=models.CASCADE)
    msg = models.TextField(blank=True)


class ReplayFile(BaseModel):
    file = models.FileField(upload_to='replay/%Y/%m/%d')

    def file_exist(self):
        return Path(self.file.path).exists()

    def on_predelete(self):
        if self.file_exist():
            Path(self.file.path).unlink()

    def __str__(self):
        return self.file.path


class ReplaySource(BaseModel):
    org_file = models.OneToOneField('replay.ReplayFile', models.DO_NOTHING, related_name='org_replay', null=True)
    file = models.OneToOneField('replay.ReplayFile', models.DO_NOTHING, related_name='replay', null=True)
    objects = ReplaySourceManager()

    class Meta:
        abstract = True

    @property
    def title(self):
        raise NotImplementedError

    @property
    def description(self):
        raise NotImplementedError

    def deleteable(self):
        deleteable = True
        if self.org_file:
            deleteable &= self.org_file.file_exist()
        if self.file:
            deleteable &= self.file.file_exist()
        return deleteable

    def on_predelete(self):
        if self.org_file:
            self.org_file.delete()
        if self.file:
            self.file.delete()


class LongReplaySource(BaseModel):
    file = models.OneToOneField('replay.ReplayFile', models.DO_NOTHING, related_name='long_replay', null=True)

    class Meta:
        abstract = True

    def on_predelete(self):
        if self.file:
            self.file.delete()


class KillReplay(ReplaySource):
    event = models.ForeignKey('event.ChampionKill', on_delete=models.SET_NULL, related_name='killreplay', null=True)
    long_file = models.ForeignKey('replay.KillLongReplay', on_delete=models.DO_NOTHING, related_name='short_files', null=True)
    ad_comment = models.CharField(blank=True, default='')

    kor_title_format = '#펜타킬 #{killer} #롤 #shorts'
    kor_description_format = '\n'.join([
        '펜타킬러 총 데미지: {total_damage}',
        '펜타킬러 총 데미지 기여도: {total_damage_contribution:.2}',
        '펜타킬 시간: {total_duration}',
    ])

    title_format = '#Pentakill #{killer} #LOL #shorts'
    description_format = '\n'.join([
        'Pentakiller Total Damage: {total_damage}',
        'Pentakiller Total Damage Contribution: {total_damage_contribution:.2}',
        'Pentakill Duration: {total_duration}',
    ])

    @property
    def title(self):
        return self.title_format.format(
            killer=self.event.killer.champion.eng_name
        )

    @property
    def description(self):
        return self.description_format.format(
            total_damage=self.event.total_damage,
            total_damage_contribution=self.event.total_damage_contribution,
            total_duration=round(self.event.duration * 5 / 1000),
        )

    def to_blacklist(self, msg):
        '''
        블랙리스트에 추가 후 삭제
        '''
        match = self.event.timeline.match
        ReplayBlackList.objects.create(
            match=match,
            msg=msg
        )
        self.org_file.upload_info.delete()
        self.delete()


class KillLongReplay(LongReplaySource):
    pass
