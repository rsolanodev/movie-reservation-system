from celery import Celery

from app.settings import settings

app = Celery("app")
app.conf.broker_url = settings.REDIS_URL
app.conf.result_backend = settings.REDIS_URL
app.conf.accept_content = ["json"]
app.conf.task_serializer = "json"
app.conf.result_serializer = "json"
app.autodiscover_tasks()
