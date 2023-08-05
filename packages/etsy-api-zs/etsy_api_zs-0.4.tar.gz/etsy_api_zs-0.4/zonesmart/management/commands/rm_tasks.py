from django.core.management.base import BaseCommand

from django_celery_beat.models import PeriodicTask


class Command(BaseCommand):
    def handle(self, **options):
        PeriodicTask.objects.all().delete()
