from django import forms
from django.contrib.admin.helpers import ActionForm
from django.db.models import Count

from replay.models import KillLongReplay


class SelectKillLongReplayActionForm(ActionForm):
    kill_long_replay = forms.ModelChoiceField(
        queryset=KillLongReplay.objects
                               .annotate(shorts_count=Count('short_files'))
                               .filter(shorts_count=0),
        required=False
    )
