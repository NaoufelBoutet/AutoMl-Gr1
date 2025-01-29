import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kaelig.settings")

celery_app = Celery("celery_kaelig")
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.autodiscover_tasks()