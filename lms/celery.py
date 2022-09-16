import os
from time import timezone
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE','lms.settings')

app = Celery('lms')
app.conf.enable_utc = False

app.conf.update(timezone = 'Asia/Kolkata')

app.config_from_object('django.conf:settings',namespace = 'CELERY')

#Celery Beat Settings
app.conf.beat_shedule = {
    'send-mail-every-day-at-9':{
        'task':'lms.tasks.send_mail_func',
        'schedule': crontab(hour=8, minute=0),
    }
}
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Hello')
