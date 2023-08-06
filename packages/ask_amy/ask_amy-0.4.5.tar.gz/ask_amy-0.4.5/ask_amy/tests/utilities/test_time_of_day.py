from ask_amy.tests.test_ask_amy_base import TestCaseASKAmy
from ask_amy.utilities.time_of_day import TimeOfDay
from unittest.mock import MagicMock
from unittest import mock

from datetime import datetime, date


class DatetimeWrapper(datetime):
    "A wrapper for datetime that can be mocked for testing."

    def __new__(cls, *args, **kwargs):
        return datetime.__new__(datetime, *args, **kwargs)


# @mock.patch('datetime.datetime', FakeDatetime)
# datetime.now = MagicMock(return_value=datetime.now())
# from datetime import datetime
# FakeDatetime.now = classmethod(lambda cls: datetime(2017, 7, 4, 12, 00, 00))

class TestTimeOfDay(TestCaseASKAmy):
    def setUp(self):
        pass

    def test_mealtime(self):
        base_time = datetime(2017, 7, 4, 12, 22, 00)
        time_adj = TimeOfDay.time_adj("05:22", "AM", base_time)

        meal_time_description = TimeOfDay.meal_time(time_adj, base_time)
        self.assertEqual(meal_time_description,'breakfast')

        time_adj = TimeOfDay.time_adj("12:22", "PM", base_time)
        meal_time_description = TimeOfDay.meal_time(time_adj, base_time)
        self.assertEqual(meal_time_description, 'lunch')

        time_adj = TimeOfDay.time_adj("05:22", "PM", base_time)
        meal_time_description = TimeOfDay.meal_time(time_adj, base_time)
        self.assertEqual(meal_time_description, 'dinner')


    def test_day_night(self):
        base_time = datetime(2017, 7, 4, 12, 22, 00)
        time_adj = TimeOfDay.time_adj("04:22", "AM", base_time)
        time_description = TimeOfDay.day_night(time_adj, base_time)
        self.assertEqual(time_description, 'night')

        time_adj = TimeOfDay.time_adj("06:22", "AM", base_time)
        time_description = TimeOfDay.day_night(time_adj, base_time)
        self.assertEqual(time_description, 'day')

        time_adj = TimeOfDay.time_adj("08:22", "PM", base_time)
        time_description = TimeOfDay.day_night(time_adj, base_time)
        self.assertEqual(time_description, 'night')

        # print("adj={} time_desc={}".format(time_adj,time_desc[tod]))

    def test_time_adj(self):
        lunch = datetime(2017, 7, 4, 12, 22, 00)
        time_adj = TimeOfDay.time_adj("11:22", "AM", lunch)
        self.assertEqual(-1, time_adj)
        time_adj = TimeOfDay.time_adj("01:22", "PM", lunch)
        self.assertEqual(1, time_adj)

    def test_utc_time_adj(self):
        lunch = datetime(2017, 7, 4, 12, 22, 00)
        time_adj = TimeOfDay.time_adj("3:54", "PM")
        now = TimeOfDay.current_time(-4)
        # print("now {}".format(now))
        us_tz_nms = ['US/Alaska', 'US/Hawaii', 'US/Arizona', 'US/Pacific', 'US/Mountain', 'US/Central', 'US/Eastern']
