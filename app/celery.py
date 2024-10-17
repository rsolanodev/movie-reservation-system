from celery import Celery

from app.settings import settings

app = Celery("app")

app.config_from_object(settings, namespace="CELERY")
app.autodiscover_tasks()
