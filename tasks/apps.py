from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'
    verbose_name = 'Tasks'

    def ready(self) -> None:
        # Import signal handlers so they are registered on app load
        try:
            import tasks.signals  # noqa: F401
        except Exception:
            # Avoid crashing on import-time issues during migrations
            pass
