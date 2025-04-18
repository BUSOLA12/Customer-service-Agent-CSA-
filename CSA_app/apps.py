from django.apps import AppConfig


class CsaAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'CSA_app'

    def ready(self):
        import CSA_app.signals