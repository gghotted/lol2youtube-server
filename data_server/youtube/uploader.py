from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

YOUTUBE_UPLOAD_SCOPE = 'https://www.googleapis.com/auth/youtube.upload'
YOUTUBE_TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

VALID_PRIVACY_STATUSES = ('public', 'private', 'unlisted')


def get_authenticated_service(
    access_token,
    refresh_token,
    client_id,
    client_secret,
    ):
    credentials = Credentials(
        access_token,
        refresh_token,
        token_uri=YOUTUBE_TOKEN_URI,
        client_id=client_id,
        client_secret=client_secret,
        scopes=[YOUTUBE_UPLOAD_SCOPE],
    )

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=credentials)


def get_upload_request(
    youtube,
    file,
    title,
    description,
    category_id,
    privacy_status,
    embeddable,
    ):
    body=dict(
        snippet=dict(
            title=title,
            description=description,
            categoryId=category_id
        ),
        status=dict(
            privacyStatus=privacy_status,
            embeddable=embeddable
        )
    )

    upload_request = youtube.videos().insert(
        part=','.join(list(body.keys())),
        body=body,
        media_body=MediaFileUpload(file, chunksize=-1)
    )
    return upload_request
