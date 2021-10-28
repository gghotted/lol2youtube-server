import signal

from match.models import Match
from summoner.models import Summoner

sigint_received = False


def sigint_handler(sig, frame):
    global sigint_received
    sigint_received = True
    print('사이클 완료후 종료됩니다.')


signal.signal(signal.SIGINT, sigint_handler)


class MatchCrawler:
    def __init__(self, break_count=float('inf')):
        self.break_count = break_count

    def __call__(self):
        while self._is_continuable():
            self._loop()

    def _loop(self):
        summoner = Summoner.objects.get_to_update()
        summoner.update_matches()

    def _is_continuable(self):
        return (Match.objects.count() < self.break_count) and (sigint_received == False)


def run():
    MatchCrawler()()


