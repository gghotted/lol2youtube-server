from match.models import Match
from summoner.models import Summoner


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
        return Match.objects.count() < self.break_count


def run():
    MatchCrawler()()


