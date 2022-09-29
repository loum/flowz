"""Date utils.

"""
import datetime
import pytz
from dateutil import tz


def utc_ymd(date_format='%Y-%m-%d') -> str:
    """Get current UTC ISO 8601 based Date.

    """
    return datetime.datetime.utcnow().strftime(date_format)


def current_local_dt(timezone='Australia/Melbourne') -> datetime:
    """Generate a *timezone* aware :class:`datetime.datetime` instance.

    Force *timezone* (don't rely on system clock).

    """
    utc = datetime.datetime.utcnow()
    utc = utc.replace(tzinfo=tz.tzutc())
    to_zone = tz.gettz(timezone)

    return utc.astimezone(to_zone)


def local_time_to_utc(local_time: str) -> datetime:
    """Convert string *local_time* to a :mod:`datetime` instance
    representing today's date int UTC.

    *local_time* is expected as human-readable form including either AM or PM.
    For example, "2:00PM" or "10:00AM".

    """
    local_dt = current_local_dt()

    if not local_time:
        naive_local_dt = datetime.datetime.strptime('00:00', '%H:%M')
    else:
        naive_local_dt = datetime.datetime.strptime(local_time, '%I:%M%p')

    local_time_utc = local_dt.replace(hour=naive_local_dt.hour,
                                      minute=naive_local_dt.minute,
                                      second=naive_local_dt.second,
                                      microsecond=naive_local_dt.microsecond)

    if local_dt.hour >= (24 - utc_offset_in_hours(local_dt)) and local_dt.hour <= 23:
        local_time_utc += datetime.timedelta(days=1)

    return local_time_utc.astimezone(pytz.utc)


def utc_offset_in_hours(date_time: datetime) -> int:
    """Helper lambda function that returns the UTC offset of ``dt`` in hours.

    """
    return int(date_time.utcoffset().total_seconds() / 60 / 60)


def local_time_to_utc_time(local_time: str = '00:00AM') -> datetime.time:
    """Convert string *local_time* to a :mod:`datetime.time` instance
    representing today's date int UTC.

    *local_time* is expected as human-readable form including either AM or PM.

    """
    return local_time_to_utc(local_time).time()


def local_time_seconds_from_now(local_time: str) -> float:
    """Calculate number of seconds between current time and *local_time*.

    Algorithm substracts *local_time* from the current time so a negative number
    implies that the *local_time* occurs in the future.  Conversely, a positive
    number implies that *local_time* has elapsed.

    """
    dt_diff = current_local_dt() - local_time_to_utc(local_time)

    return dt_diff.total_seconds()
