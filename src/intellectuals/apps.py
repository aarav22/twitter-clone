from django.apps import AppConfig


class IntellectualsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'intellectuals'
    def ready(self):
        import intellectuals.signals