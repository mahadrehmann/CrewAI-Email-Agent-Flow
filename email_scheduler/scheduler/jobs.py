# scheduler/jobs.py

import logging
from datetime import datetime
from .models import Schedule
from emailcrew.main import run_crew_and_send_mail

logger = logging.getLogger(__name__)

def check_and_send():
    now = datetime.now()
    weekday = now.strftime("%A").lower()
    current_time = now.time().replace(second=0, microsecond=0)

    due_qs = Schedule.objects.filter(
        active=True,
        day=weekday,
        time=current_time
    )
    for sched in due_qs:
        try:
            run_crew_and_send_mail(sched.receiver, sched.filepath)
            logger.info(f"Sent scheduled email for {sched.user.username} at {current_time}")
        except Exception as e:
            logger.error(f"Error sending email for {sched.user.username}: {e}")
