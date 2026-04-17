from django.apps import AppConfig


class SelectionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dvadmin.selection'
    verbose_name = "缠论选股模块"

    def ready(self):
        # 没有 signals
        pass
