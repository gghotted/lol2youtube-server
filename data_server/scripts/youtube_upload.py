import time

import schedule
from django.conf import settings
from youtube.models import UploadInfo


def upload():
    for info in list(UploadInfo.objects.wait_upload()):
        print(f'{info.pk}를 업로드합니다.')
        info.upload()


def run():
    schedule.every(1).minutes.do(upload)
    while True:
        schedule.run_pending()
        time.sleep(1)
