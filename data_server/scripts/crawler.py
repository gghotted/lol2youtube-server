import signal

from data_cleaner.json_data import JsonDataCleaner
from django.conf import settings
from match.models import Match
from raw_data.models import JsonData
from summoner.models import Summoner

sigint_received = False


def sigint_handler(sig, frame):
    global sigint_received
    sigint_received = True
    print('사이클 완료후 종료됩니다.')


# signal.signal(signal.SIGINT, sigint_handler)


class MatchCrawler:
    def __init__(self, break_count=float('inf')):
        self.break_count = break_count
        self.loop_count = 0
        self.clean_data_loop_count = settings.CLEAN_DATA_LOOP_COUNT

    def __call__(self):
        self._preprocess()
        while self._is_continuable():
            if self.loop_count % self.clean_data_loop_count == 0:
                JsonDataCleaner().clean()
            self._loop()
            self.loop_count += 1

    def _delete_invalid_data(self, queryset, name):
        count = queryset.filter(parse_success=False).delete()[0]
        print(f'유효하지 않은 {name} {count}개를 삭제했습니다.')

    def _preprocess(self):
        self._delete_invalid_data(JsonData.objects.matches(), '매치')
        self._delete_invalid_data(JsonData.objects.summoners(), '소환사')
        self._delete_invalid_data(JsonData.objects.timelines(), '타임라인')

    def _loop(self):
        summoner = Summoner.objects.get_to_update()
        summoner.update_matches()

    def _is_continuable(self):
        return (Match.objects.count() < self.break_count) and (sigint_received == False)


def run():
    MatchCrawler()()
