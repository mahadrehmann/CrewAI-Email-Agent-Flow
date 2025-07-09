# scheduler/apps.py

import logging
import sys
from django.apps import AppConfig

logger = logging.getLogger(__name__)

class SchedulerConfig(AppConfig):
    name = 'scheduler'

    def ready(self):
        # 1) Don’t start the scheduler when running migrations (or makemigrations, collectstatic, test, shell, etc.)
        cmd = sys.argv[1] if len(sys.argv) > 1 else ''
        if cmd in ('migrate', 'makemigrations', 'collectstatic', 'shell', 'test'):
            return

        # 1) Enable WAL mode for SQLite to reduce locking contention
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("PRAGMA journal_mode=WAL;")
                logger.info("✅ SQLite switched to WAL mode")
        except Exception as e:
            logger.warning(f"Could not set WAL mode: {e}")


        # 2) Now it’s safe to import APScheduler jobstore and your job
        # from django_apscheduler.jobstores import DjangoJobStore
        from apscheduler.schedulers.background import BackgroundScheduler
        from .jobs import check_and_send

        # 3) Only start one scheduler
        if not hasattr(self, 'scheduler_started'):
            scheduler = BackgroundScheduler()
            # scheduler.add_jobstore(DjangoJobStore(), "default")
            # scheduler.start()

            # run check_and_send() every minute
            scheduler.add_job(
                check_and_send,
                trigger='cron',
                minute='*',
                id='scheduler_poll_db',
                replace_existing=True,
            )
            scheduler.start()
            logger.info("🤖 APScheduler started — polling every minute.")
            self.scheduler_started = True
