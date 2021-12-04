from common.models import BaseModel
from django.db import models
from youtube.models import ChannelGroup, UploadInfo

from replay.managers import ReplaySourceManager


class ReplayBlackList(BaseModel):
    match = models.ForeignKey('match.Match', on_delete=models.CASCADE)
    msg = models.TextField(blank=True)


class ReplayFile(BaseModel):
    file = models.FileField(upload_to='replay/%Y/%m/%d')

    def delete_file(self):
        ...


class ReplaySource(BaseModel):
    file = models.OneToOneField('replay.ReplayFile', models.DO_NOTHING, related_name='replay')
    link = models.URLField(blank=True)
    objects = ReplaySourceManager()

    class Meta:
        abstract = True

    @property
    def title(self):
        raise NotImplementedError

    @property
    def description(self):
        raise NotImplementedError

    @property
    def channel_group_name(self):
        raise NotImplementedError

    def set_wait_upload(self):
        channel_group, _ = ChannelGroup.objects.get_or_create(
            name=self.channel_group_name,
            defaults={'description': '추가 바람'},
        )
        UploadInfo.objects.create(
            channel_group=channel_group,
            file=self.file,
            title=self.title,
            description=self.description,
        )


class KillReplay(ReplaySource):
    event = models.ForeignKey('event.ChampionKill', on_delete=models.DO_NOTHING, related_name='killreplay')

    title_format = '#펜타킬 #{killer} #롤 #shorts'
    description_format = '\n'.join([
        '펜타킬 총 데미지: {total_damage}',
        '펜타킬 평균 데미지 기여도: {total_damage_contribution:.2}',
    ])

    @property
    def channel_group_name(self):
        return '펜타킬 모음'

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
