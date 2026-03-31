from django.apps import AppConfig


class KisanappConfig(AppConfig):
    name = 'kisanapp'

    def ready(self):
        import kisanapp.models  # noqa — triggers signal registration
