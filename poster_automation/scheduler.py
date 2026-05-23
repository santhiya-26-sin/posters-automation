import time
from datetime import datetime, timedelta
from .logger import log
from .config import CONFIG

def wait_until_scheduled_time(hour=None, minute=None):
    hour   = hour   if hour   is not None else CONFIG["schedule_hour"]
    minute = minute if minute is not None else CONFIG["schedule_minute"]

    now    = datetime.now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # If time already passed today, schedule for tomorrow
    if target <= now:
        target += timedelta(days=1)

    wait_sec = (target - now).total_seconds()
    wait_min = round(wait_sec / 60)

    log(f"Scheduled time: {hour}:{str(minute).zfill(2)}")
    log(f"Waiting {wait_min} minute(s)... Next run: {target.strftime('%Y-%m-%d %H:%M:%S')}")

    time.sleep(wait_sec)
    log("Scheduled time reached! Starting workflow...")
