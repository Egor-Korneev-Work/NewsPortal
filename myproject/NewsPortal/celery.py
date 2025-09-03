from celery.schedules import crontab

app.conf.beat_schedule = {
    'send-weekly-notifications': {
        'task': 'news.tasks.send_weekly_notifications',
        'schedule': crontab(day_of_week='sun', hour=0, minute=0),
    },
}