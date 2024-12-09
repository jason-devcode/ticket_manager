from django.apps import AppConfig
from django.db.models.signals import post_migrate


class DjangopwaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "djangopwa"
    verbose_name = "Aplicacion sorteos"

    def ready(self):
        from .groups import create_seller_group_with_permissions
        post_migrate.connect(create_seller_group_with_permissions, sender=self)
