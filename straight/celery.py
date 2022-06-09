from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'straight.settings')
app = Celery('straight', backend='redis://localhost:6379', broker='redis://localhost:6379')
app.conf.enable_utc = True

app.config_from_object('django.conf:settings', namespace='CELERY')

#Celery beat settings
app.conf.update(result_expires=3600, enable_utc=True, timezone='Asia/Jakarta')
app.conf.beat_schedule = {
    'test': {
        'task': 'straight.tasks.test_func',
        'schedule': crontab(),
    }
}
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))