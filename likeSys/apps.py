from django.apps import AppConfig


class LikeSysConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'likeSys'
    
    def ready(self):
        import likeSys.signals  