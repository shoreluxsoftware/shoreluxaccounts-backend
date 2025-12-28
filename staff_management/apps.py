from django.apps import AppConfig

class StaffManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'staff_management'

    def ready(self):
        # import signals so Django registers them
        import staff_management.signals  # noqa