from datetime import datetime as dt

from pytz import timezone

# EU/Rome timezone
EU_ROME_TZ = timezone("Europe/Rome")


def get_current_time():
    """
    Returns the current date and time (Europe/Rome timezone).
    """

    rome_now = dt.now(EU_ROME_TZ).strftime("%d/%m/%Y %H:%M:%S")
    return rome_now


def timestamp_to_hms(timestamp):
    return dt.fromtimestamp(timestamp, tz=EU_ROME_TZ).strftime("%H:%M:%S")
