import time
from datetime import datetime, timedelta

import requests
from django.conf import settings
from requests.exceptions import ConnectionError

from raw_data.exceptions import JsonDataAlreadyExist
from raw_data.models import APICallInfo, JsonData

api_keys = settings.RIOT_API_KEYS


class APIKey:
    def __init__(self, key):
        self.key = key
        self.usable_time = datetime.min
    
    @property
    def is_usable(self):
        return datetime.now() > self.usable_time

    def rest(self, sec):
        sec += 5
        self.usable_time = datetime.now() + timedelta(seconds=sec)

    def __str__(self):
        return self.key


class APIKeyManager:
    def __init__(self, keys):
        self.keys = [APIKey(key) for key in keys]
    
    def get_usable_key(self):
        key = list(sorted(self.keys, key=lambda k: k.usable_time))[0]
        if datetime.now() > key.usable_time:
            return key
        else:
            wait_time = (key.usable_time - datetime.now()).seconds
            print(f'api key를 사용하기위해 {wait_time}초 기다립니다.')
            time.sleep(wait_time)
            return key


class APIResource:
    endpoint = None
    region = None
    api_limit_minutes = 2
    api_limit_count = 200

    def __init__(self):
        self.response = None
        self.json = None
        self.call_info = None
        self.json_data_obj = None
        self.apikey_manager = APIKeyManager(api_keys)
        self.apikey = None

    @property
    def host(self):
        return f'https://{self.region}.api.riotgames.com'

    @property
    def url(self):
        return self.host + self.endpoint

    @property
    def headers(self):
        self.apikey = self.apikey_manager.get_usable_key()
        return {'X-Riot-Token': str(self.apikey)}

    def get(self, try_count=0, **kwargs):
        try:
            kwargs.setdefault('headers', {})
            kwargs['headers'].update(self.headers)
            return requests.get(self.url, **kwargs)
        except ConnectionError:
            if try_count == 5:
                raise ConnectionError
            return self.get(try_count=try_count + 1, **kwargs)

    def __call__(self):
        self._check_already_exist()
        self.response = self.get()

        if self.response.status_code == 429:
            return self._retry_call()

        self.json = self.response.json()
        self.call_info = self._save_call_info()
        print(f'{self.url}에 요청을 완료')
        return self

    def _check_already_exist(self):
        json_data = JsonData.objects.exclude(api_info=None).filter(api_info__url=self.url)
        if json_data.exists():
            self.json_data_obj = json_data.first()
            raise JsonDataAlreadyExist('이미 존재하는 데이터 입니다.')

    def _retry_call(self):
        wait_time = int(self.response.headers['retry-after'])
        self.apikey.rest(wait_time)
        return self()

    def _save_call_info(self):
        return APICallInfo.objects.create(
            type=self.api_name,
            url=self.url,
        )

    def save_to_db(self):
        return JsonData.objects.create(
            data=self.response.json(),
            api_info=self.call_info
        )


class MatchAPI(APIResource):
    api_name = 'match'
    region = 'asia'

    def __init__(self, match_id, **kwargs):
        super().__init__(**kwargs)
        self.match_id = match_id

    @property
    def endpoint(self):
        return f'/lol/match/v5/matches/{self.match_id}'


class MatchListAPI(APIResource):
    api_name = 'match_list'
    region = 'asia'

    def __init__(self, puuid, **kwargs):
        super().__init__(**kwargs)
        self.puuid = puuid

    @property
    def endpoint(self):
        from match.models import Version

        start_time = (int(
            Version.objects.latest_version()
            .matches.order_by('game_creation')
            .first().game_creation.timestamp()
        ))
        queue = settings.MATCH_LIST_QUEUE_ID
        count = settings.MATCH_LIST_COUNT
        return (f'/lol/match/v5/matches/by-puuid/{self.puuid}/ids'
                f'?queue={queue}&count={count}&startTime={start_time}')


class TimelineAPI(APIResource):
    api_name = 'timeline'
    region = 'asia'

    def __init__(self, match_id, **kwargs):
        super().__init__(**kwargs)
        self.match_id = match_id

    @property
    def endpoint(self):
        return f'/lol/match/v5/matches/{self.match_id}/timeline'


class SummonerAPI(APIResource):
    api_name = 'summoner'
    region = 'kr'

    def __init__(self, name=None, puuid=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.puuid = puuid

    @property
    def endpoint(self):
        if self.name:
            return f'/lol/summoner/v4/summoners/by-name/{self.name}'
        if self.puuid:
            return f'/lol/summoner/v4/summoners/by-puuid/{self.puuid}'
