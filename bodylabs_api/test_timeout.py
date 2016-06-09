import unittest, signal, os
from bodylabs_api.timeout import Timeout, TimeoutError

class TestTimeoutContextManager(unittest.TestCase):
    TEST_KWARGS_LIST = [
        {},
        {'seconds': 5},
        {'minutes': 5},
        {'hours': 5},
        {'seconds': 5, 'minutes': 5},
        {'seconds': 5, 'hours': 5},
        {'minutes': 5, 'hours': 5},
        {'seconds': 5, 'minutes': 5, 'hours': 5}
    ]

    TEST_ARGS_LIST = [
        [None],
        [],
        [5],
        [5, 5],
        [5, 5, 5],
    ]

    @staticmethod
    def total_seconds(seconds=None, minutes=None, hours=None):
        if seconds is None:
            seconds = 0
        if minutes is None:
            minutes = 0
        if hours is None:
            hours = 0
        return hours * 3600 + minutes * 60 + seconds

    def test_timeout_timer_is_set_correctly_with_args(self):
        for test_args in self.TEST_ARGS_LIST:
            with Timeout(*test_args):
                # turns off timer and returns the previous setting in seconds
                set_number_of_seconds = signal.alarm(0)
            expected_number_of_seconds = self.total_seconds(*test_args)
            self.assertEqual(set_number_of_seconds, expected_number_of_seconds)

    def test_timeout_timer_is_set_correctly_with_kwargs(self):
        for test_kwargs in self.TEST_KWARGS_LIST:
            with Timeout(**test_kwargs):
                # turns off timer and returns the previous setting in seconds
                set_number_of_seconds = signal.alarm(0)
            expected_number_of_seconds = self.total_seconds(**test_kwargs)
            self.assertEqual(set_number_of_seconds, expected_number_of_seconds)

    def test_timeout_raises_timeout_error(self):
        def will_time_out():
            from time import sleep
            with Timeout(1):
                sleep(2) # Seems appropriate to have at least one real timeout
        self.assertRaises(TimeoutError, will_time_out)

    def test_timeout_does_not_raise_on_clean_exit(self):
        def will_not_time_out():
            with Timeout(hours=1):
                return 'a_random_return_value'
        self.assertEqual('a_random_return_value', will_not_time_out())
