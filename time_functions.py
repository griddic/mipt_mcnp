__author__ = 'griddic'

import time
from datetime import datetime


def time_now():
    """Return GMT rounded to seconds.
    """
    return datetime(*time.gmtime()[:6])


def stamp_Ymd(t=time_now()):
    return t.strftime("%Y%m%d")


def time_to_str(time_):
    return str(time_)


class Stopwatch(object):
    def __init__(self):
        self.start()
        pass

    def start(self):
        self._start = time_now()

    def stop(self, type_='date_time diff'):
        """ type='sec' if you want measurement in seconds. """
        if type_ == 'sec':
            return (time_now() - self._start).total_seconds()
        return time_now() - self._start

    def restart(self, type_='date_time diff'):
        duration = self.stop(type_)
        self.start()
        return duration
