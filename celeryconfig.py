from datetime import timedelta
from celery.schedules import crontab

BROKER_URL = 'redis://redis:6379/1'

# run everyday at 10:30 AM UTC (4 PM IST)
CELERYBEAT_SCHEDULE = {
    'run-everyday-at-4pm': {
        'task': 'tasks.daily_task_to_schedule',
        'schedule': crontab(minute=30, hour=10)
    }
}