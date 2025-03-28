import calendar
import datetime
from calendar import monthrange

from check_missing_dates import find_missing_dates


def test_find_missing_dates():
    today = datetime.datetime.today()
    next_month = today.replace(day=1) + datetime.timedelta(days=32)
    month = next_month.month
    year = next_month.year
    days_in_month = monthrange(year, month)[1]

    first_day_of_month = next_month.replace(day=1).strftime('%Y-%m-%d')
    third_day_of_month = next_month.replace(day=3).strftime('%Y-%m-%d')
    fifth_day_of_month = next_month.replace(day=5).strftime('%Y-%m-%d')

    dates_in_db = {first_day_of_month, third_day_of_month, fifth_day_of_month}

    result = find_missing_dates(dates_in_db, days_in_month, month, year, today)

    expected_missing_dates = []
    for day in range(1, days_in_month + 1):
        date_str = next_month.replace(day=day).strftime('%Y-%m-%d')
        if date_str not in dates_in_db:
            expected_missing_dates.append(date_str)

    # The missing dates should be all dates of the given month that are not the dates of the given month in the database
    assert result == expected_missing_dates

def test_find_missing_dates_of_different_months():
    result = []
    expected_result = []

    today = datetime.datetime.today()
    month = today.month
    year = today.year

    for i in range(1, 3):
        month += i

        if month > 12:
            month = 1
            year += 1

        days_in_month = monthrange(year, month)[1]

        date1 = datetime.date(year, month, 1).strftime('%Y-%m-%d')
        date2 = datetime.date(year, month, 5).strftime('%Y-%m-%d')

        dates_in_db = {date1, date2}
        result += find_missing_dates(dates_in_db, days_in_month, month, year, today)

        for day in range(1, days_in_month + 1):
            date_str = datetime.datetime(year, month, day).strftime('%Y-%m-%d')
            if date_str not in dates_in_db:
                expected_result.append(date_str)

    assert result == expected_result


def test_handles_empty_set_of_dates():
    # Given
    dates_in_db = set()
    days_in_month = 30
    today = datetime.datetime.today()
    month = 9
    year = today.year + 1

    # When
    missing_dates = find_missing_dates(dates_in_db, days_in_month, month, year, today)
    expected_missing_dates = [datetime.datetime(year, month, day).strftime('%Y-%m-%d')
                              for day in range(1, days_in_month + 1)]
    # The missing dates should be all dates of the given month that are not the dates of the given month in the database
    assert missing_dates == expected_missing_dates


def test_handles_leap_year_feb_missing_dates():
    # Given
    today = datetime.datetime.today()
    month = 2
    year = today.year + 1
    dates_in_db = {f'{year}-02-01', f'{year}-02-02', f'{year}-02-03', f'{year}-02-04', f'{year}-02-06'}

    # Determine the number of days in February for the given year
    if calendar.isleap(year):
        days_in_month = 29
    else:
        days_in_month = 28

    # When
    missing_dates = find_missing_dates(dates_in_db, days_in_month, month, year, today)

    expected_missing_dates = []
    for day in range(1, days_in_month + 1):
        date_str = datetime.datetime(year, month, day).strftime('%Y-%m-%d')
        if date_str not in dates_in_db:
            expected_missing_dates.append(date_str)

    # The missing dates should be all dates of the given month that are not the dates of the given month in the database
    assert missing_dates == expected_missing_dates


def test_past_dates_in_db():
    today = datetime.datetime.today()
    dates_in_db = {'2020-03-01', '2020-03-02', '2020-03-03', '2020-03-04'}
    days_in_month = 31
    month = 3
    year = 2020
    missing_dates = find_missing_dates(dates_in_db, days_in_month, month, year, today)

    assert missing_dates == []