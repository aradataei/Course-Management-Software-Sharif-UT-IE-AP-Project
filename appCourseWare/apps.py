from django.apps import AppConfig


class AppcoursewareConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appCourseWare'

    def ready(self):
        import appCourseWare.signals  # Replace with your actual app name