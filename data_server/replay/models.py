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
        Path(self.file.path).unlink()


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

    def set_wait_upload(self):
        UploadInfo.objects.create(
            file=self.file,
            title=self.title,
            description=self.description,
        )

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
    event = models.ForeignKey('event.ChampionKill', on_delete=models.DO_NOTHING, related_name='killreplay')
    long_file = models.ForeignKey('replay.KillLongReplay', on_delete=models.DO_NOTHING, related_name='short_files', null=True)

    title_format = '#PentaKill #{killer} #LOL #shorts'
    description_format = '\n'.join([
        'Total Damage: {total_damage}',
        'Total Damage Contribution: {total_damage_contribution:.2}',
    ])

    @property
    def title(self):
        return self.title_format.format(
            killer=self.event.killer.get_champion()
        )

    @property
    def description(self):
        return self.description_format.format(
            total_damage=self.event.total_damage,
            total_damage_contribution=self.event.total_damage_contribution,
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
        self.delete()


class KillLongReplay(LongReplaySource):
    pass
