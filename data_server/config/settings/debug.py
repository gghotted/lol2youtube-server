from .base import *

DEBUG_SECRET = json.loads(SECRET_DEBUG_FILE.read_text())

DEBUG = DEBUG_SECRET['debug']

ALLOWED_HOSTS = DEBUG_SECRET['allowed_hosts']

DATABASES = {'default': DEBUG_SECRET['databases']}

WSGI_APPLICATION = 'config.wsgi.debug.application'
