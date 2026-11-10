"""In-memory operational counters (reset on process restart)."""
from datetime import datetime, timezone
from time import monotonic

STARTED = monotonic()
COUNTERS = {"received": 0, "matched": 0, "sent": 0, "failed": 0, "filtered": 0}
LAST_MESSAGE_AT = None
LAST_SENT_AT = None


def record_received():
    global LAST_MESSAGE_AT
    COUNTERS["received"] += 1
    LAST_MESSAGE_AT = datetime.now(timezone.utc)


def record_sent():
    global LAST_SENT_AT
    COUNTERS["sent"] += 1
    LAST_SENT_AT = datetime.now(timezone.utc)


def fmt_time(value):
    return value.strftime("%Y-%m-%d %H:%M:%S UTC") if value else "Never"


def uptime():
    seconds = int(monotonic() - STARTED)
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days}d {hours}h {minutes}m {seconds}s" if days else f"{hours}h {minutes}m {seconds}s"
