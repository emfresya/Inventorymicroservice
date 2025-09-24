import os
from celery import Celery

celery_app = Celery(
    'inventory_tasks',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0'),
    include=['app.tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    beat_schedule={
        'update-monthly-sales-hourly': {
            'task': 'app.tasks.update_monthly_sales_task',
            'schedule': 120.0,  # раз в час
        },
    }
)