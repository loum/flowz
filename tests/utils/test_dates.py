"""Unit test cases for :module:`dagster.utils.dates`.
"""
import datetime
import unittest.mock
import pytz

import dagster.utils.dates


@unittest.mock.patch('dagster.utils.dates.datetime')
def test_utc_ymd(mock_time):
    """Simulate UTC YYYY-MM-DS behaviour.
    """
    # Given a point in time before rollover time
    mock_time.datetime.utcnow.return_value = datetime.datetime(2020, 5, 10, 14, 59, 59)

    # when I derive the UTC ISO 8601 date
    received = dagster.utils.dates.utc_ymd()

    # then I should received a properly formated date string
    assert received == '2020-05-10', 'UTC ISO 8601 date error'


@unittest.mock.patch('dagster.utils.dates.datetime')
def test_current_local_dt_pre_tz_rollover(mock_time):
    """Test Melbourne time pre-TZ rollover.
    """
    # Given a point in time before Melbourne rollover time
    # (Wednesday, December 1, 2021 23:59:59 GMT+11:00)
    mock_time.datetime.utcnow.return_value = datetime.datetime.strptime('2021-12-01 12:59:59',
                                                                        '%Y-%m-%d %H:%M:%S')

    # when I derive local Melbourne based time
    received = dagster.utils.dates.current_local_dt()

    # then I should received a properly formated date string
    assert received.strftime('%Y-%m-%d') == '2021-12-01', 'Melbourne time pre-TZ rollover error'


@unittest.mock.patch('dagster.utils.dates.datetime')
def test_current_local_dt_pre_utc_rollover(mock_time):
    """Test Melbourne time pre-UTC rollover.
    """
    # Given a point in time before UTC rollover time
    # Thursday, December 1, 2021 10:59:59 GMT+11:00
    mock_time.datetime.utcnow.return_value = datetime.datetime.strptime('2021-12-01 10:59:59',
                                                                        '%Y-%m-%d %H:%M:%S')


    # when I derive local Melbourne based time
    received = dagster.utils.dates.current_local_dt()

    # then I should received a properly formated date string
    assert received.strftime('%Y-%m-%d') == '2021-12-01', 'Melbourne time pre-UTC rollover error'


@unittest.mock.patch('dagster.utils.dates.datetime')
def test_current_local_dt_post_utc_rollover(mock_time):
    """Test Melbourne time post-UTC rollover.
    """
    # Given a point in time after UTC rollover time
    # Thursday, December 2, 2021 11:00:01 GMT+11:00
    mock_time.datetime.utcnow.return_value = datetime.datetime.strptime('2021-12-02 0:0:01',
                                                                        '%Y-%m-%d %H:%M:%S')

    # when I derive local Melbourne based time
    received = dagster.utils.dates.current_local_dt()

    # then I should received a properly formated date string
    assert received.strftime('%Y-%m-%d') == '2021-12-02', 'Melbourne time post-UTC rollover error'


@unittest.mock.patch('dagster.utils.dates.datetime')
def test_current_local_dt_post_tz_rollover(mock_time):
    """Test Melbourne time post-TZ rollover.
    """
    # Given a point in time after Melbourne rollover time
    # (Wednesday, December 3, 2021 0:0:01 GMT+11:00)
    mock_time.datetime.utcnow.return_value = datetime.datetime.strptime('2021-12-02 13:00:01',
                                                                        '%Y-%m-%d %H:%M:%S')

    # when I derive local Melbourne based time
    received = dagster.utils.dates.current_local_dt()

    # then I should received a properly formated date string
    assert received.strftime('%Y-%m-%d') == '2021-12-03', 'Melbourne time post-TZ rollover error'


@unittest.mock.patch('dagster.utils.dates.current_local_dt')
def test_local_time_to_utc_time(mock_time):
    """Local time to UTC: pre-UTC rollover.
    """
    # Given a point in time
    _dt = datetime.datetime(2020, 5, 10, 15, 0, 1)
    mock_time.return_value = pytz.timezone('Australia/Melbourne').localize(_dt)

    # and a local time string
    local_time = '9:00AM'

    # when I convert to a UTC-based datetime object
    received = dagster.utils.dates.local_time_to_utc_time(local_time=local_time)

    # then expected result should be
    msg = 'Local time string to UTC datetime.time error'
    assert received == datetime.time(23, 0), msg


@unittest.mock.patch('dagster.utils.dates.utc_offset_in_hours')
@unittest.mock.patch('dagster.utils.dates.current_local_dt')
def test_local_am_time_to_utc_pre_utc_rollover_same_date_as_local(mock_time, mock_utc_offset):
    """Local AM time to UTC: pre-UTC rollover.
    """
    # Given a point in UTC time with same date as local time string
    _dt = datetime.datetime(2021, 1, 21, 12, 59)
    mock_time.return_value = pytz.timezone('Australia/Melbourne').localize(_dt)
    mock_utc_offset.return_value = 11 # AEDT.

    # and a local AM time string
    local_time = '4:30AM'

    # when I convert the local time string to a UTC-based datetime object
    received = dagster.utils.dates.local_time_to_utc(local_time=local_time)

    # then expected result should be
    msg = 'Local time string to UTC datetime error'
    assert received == datetime.datetime(2021, 1, 20, 17, 30, tzinfo=pytz.UTC), msg


@unittest.mock.patch('dagster.utils.dates.utc_offset_in_hours')
@unittest.mock.patch('dagster.utils.dates.current_local_dt')
def test_local_pm_time_to_utc_pre_utc_rollover_same_date_as_local(mock_time, mock_utc_offset):
    """Local PM time to UTC: pre-UTC rollover.
    """
    # Given a point in UTC time with same date as local time string
    _dt = datetime.datetime(2021, 1, 21, 12, 59)
    mock_time.return_value = pytz.timezone('Australia/Melbourne').localize(_dt)
    mock_utc_offset.return_value = 11 # AEDT.

    # and a local PM time string
    local_time = '4:30PM'

    # when I convert the local time string to a UTC-based datetime object
    received = dagster.utils.dates.local_time_to_utc(local_time=local_time)

    # then expected result should be
    msg = 'Local time string to UTC datetime error'
    assert received == datetime.datetime(2021, 1, 21, 5, 30, tzinfo=pytz.UTC), msg


@unittest.mock.patch('dagster.utils.dates.utc_offset_in_hours')
@unittest.mock.patch('dagster.utils.dates.current_local_dt')
def test_local_am_time_to_utc_pre_utc_rollover_local_date_greater_am(mock_time, mock_utc_offset):
    """Local AM time to UTC: UTC time and local time in the next day.
    """
    # Given a point in UTC time and local time in the next day
    _dt = datetime.datetime(2021, 1, 21, 13, 0)
    mock_time.return_value = pytz.timezone('Australia/Melbourne').localize(_dt)
    mock_utc_offset.return_value = 11 # AEDT.

    # and a local AM time string
    local_time = '4:30AM'

    # when I convert the local time string to a UTC-based datetime object
    received = dagster.utils.dates.local_time_to_utc(local_time=local_time)

    # then expected result should be
    msg = 'Local time string to UTC datetime error'
    assert received == datetime.datetime(2021, 1, 21, 17, 30, tzinfo=pytz.UTC), msg


@unittest.mock.patch('dagster.utils.dates.utc_offset_in_hours')
@unittest.mock.patch('dagster.utils.dates.current_local_dt')
def test_local_pm_time_to_utc_pre_utc_rollover_local_date_greater(mock_time, mock_utc_offset):
    """Local PM time to UTC: UTC time and local time in the next day.
    """
    # Given a point in UTC time and local time in the next day
    _dt = datetime.datetime(2021, 1, 21, 13, 0)
    mock_time.return_value = pytz.timezone('Australia/Melbourne').localize(_dt)
    mock_utc_offset.return_value = 11 # AEDT.

    # and a local PM time string
    local_time = '4:30PM'

    # when I convert the local time string to a UTC-based datetime object
    received = dagster.utils.dates.local_time_to_utc(local_time=local_time)

    # then expected result should be
    msg = 'Local time string to UTC datetime error'
    assert received == datetime.datetime(2021, 1, 22, 5, 30, tzinfo=pytz.UTC), msg


@unittest.mock.patch('dagster.utils.dates.utc_offset_in_hours')
@unittest.mock.patch('dagster.utils.dates.current_local_dt')
def test_local_am_time_to_utc_pre_utc_rollover_at_23_59_local_date_greater(mock_time,
                                                                           mock_utc_offset):
    """Local AM time to UTC: UTC time and local time in the next day.
    """
    # Given a point in UTC time and local time in the next day
    _dt = datetime.datetime(2021, 1, 21, 23, 59)
    mock_time.return_value = pytz.timezone('Australia/Melbourne').localize(_dt)
    mock_utc_offset.return_value = 11 # AEDT.

    # and a local AM time string
    local_time = '4:30AM'

    # when I convert the local time string to a UTC-based datetime object
    received = dagster.utils.dates.local_time_to_utc(local_time=local_time)

    # then expected result should be
    msg = 'Local time string to UTC datetime error'
    assert received == datetime.datetime(2021, 1, 21, 17, 30, tzinfo=pytz.UTC), msg


@unittest.mock.patch('dagster.utils.dates.utc_offset_in_hours')
@unittest.mock.patch('dagster.utils.dates.current_local_dt')
def test_local_pm_time_to_utc_pre_utc_rollover_at_23_59_local_date_greater(mock_time,
                                                                           mock_utc_offset):
    """Local PM time to UTC: UTC time and local time in the next day.
    """
    # Given a point in UTC time and local time in the next day
    _dt = datetime.datetime(2021, 1, 21, 23, 59)
    mock_time.return_value = pytz.timezone('Australia/Melbourne').localize(_dt)
    mock_utc_offset.return_value = 11 # AEDT.

    # and a local PM time string
    local_time = '4:30PM'

    # when I convert the local time string to a UTC-based datetime object
    received = dagster.utils.dates.local_time_to_utc(local_time=local_time)

    # then expected result should be
    msg = 'Local time string to UTC datetime error'
    assert received == datetime.datetime(2021, 1, 22, 5, 30, tzinfo=pytz.UTC), msg


@unittest.mock.patch('dagster.utils.dates.utc_offset_in_hours')
@unittest.mock.patch('dagster.utils.dates.current_local_dt')
def test_local_am_time_to_utc_and_utc_rollover_same_date_as_local(mock_time, mock_utc_offset):
    """Local AM time to UTC: UTC time with same local time date.
    """
    # Given a point in UTC time with same local time date
    _dt = datetime.datetime(2021, 1, 22, 0, 0)
    mock_time.return_value = pytz.timezone('Australia/Melbourne').localize(_dt)
    mock_utc_offset.return_value = 11 # AEDT.

    # and a local AM time string
    local_time = '4:30AM'

    # when I convert the local time string to a UTC-based datetime object
    received = dagster.utils.dates.local_time_to_utc(local_time=local_time)

    # then expected result should be
    msg = 'Local time string to UTC datetime error'
    assert received == datetime.datetime(2021, 1, 21, 17, 30, tzinfo=pytz.UTC), msg


@unittest.mock.patch('dagster.utils.dates.utc_offset_in_hours')
@unittest.mock.patch('dagster.utils.dates.current_local_dt')
def test_local_pm_time_to_utc_and_utc_rollover_same_date_as_local(mock_time, mock_utc_offset):
    """Local PM time to UTC: UTC time with same local time date.
    """
    # Given a point in UTC time with same local time date
    _dt = datetime.datetime(2021, 1, 22, 0, 0)
    mock_time.return_value = pytz.timezone('Australia/Melbourne').localize(_dt)
    mock_utc_offset.return_value = 11 # AEDT.

    # and a local PM time string
    local_time = '4:30PM'

    # when I convert the local time string to a UTC-based datetime object
    received = dagster.utils.dates.local_time_to_utc(local_time=local_time)

    # then expected result should be
    msg = 'Local time string to UTC datetime error'
    assert received == datetime.datetime(2021, 1, 22, 5, 30, tzinfo=pytz.UTC), msg


@unittest.mock.patch('dagster.utils.dates.current_local_dt')
def test_local_time_seconds_from_now_future(mock_time):
    """Local time seconds from now (mock): local time occurs in the future.
    """
    # Given a point in time (local time)
    mock_time.side_effect = [
        pytz.timezone('Australia/Melbourne').localize(datetime.datetime(2020, 12, 1, 14, 53, 4)),
        pytz.timezone('Australia/Melbourne').localize(datetime.datetime(2020, 12, 1, 3, 53, 5))
    ]

    # and a local time string
    local_time = '02:54PM'

    # when I calculate the number of seconds
    received = dagster.utils.dates.local_time_seconds_from_now(local_time=local_time)

    # then expected result should be
    msg = 'Local time seconds from now error: local time occurs in the future'
    assert received == -56.0, msg


@unittest.mock.patch('dagster.utils.dates.current_local_dt')
def test_local_time_seconds_from_now_past(mock_time):
    """Local time seconds from now (mock): local time occurs in the future.
    """
    # Given a point in time (local time)
    mock_time.side_effect = [
        pytz.timezone('Australia/Melbourne').localize(datetime.datetime(2020, 12, 1, 14, 53, 4)),
        pytz.timezone('Australia/Melbourne').localize(datetime.datetime(2020, 12, 1, 3, 53, 5))
    ]

    # and a local time string
    local_time = '02:53PM'

    # when I calculate the number of seconds
    received = dagster.utils.dates.local_time_seconds_from_now(local_time=local_time)

    # then expected result should be
    msg = 'Local time seconds from now error: local time occurs in the past'
    assert received == 4.0, msg
