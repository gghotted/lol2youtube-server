from django.apps import AppConfig


class ReplayConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'replay'

    def ready(self):
        from replay import signals
