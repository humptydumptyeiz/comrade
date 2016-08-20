import datetime
import time
import io

import pytz
from twisted.logger import Logger, LimitedHistoryLogObserver, FileLogObserver
from twisted.python.logfile import DailyLogFile

from utils import defaults as CONST


time_format = "%Y-%m-%d %H:%M:%S:%f"


class LimitedLogger(object):
    """
    Mixin class for logging.
    """

    def __init__(self):
        self.temp_log = Logger(observer=LimitedHistoryLogObserver(20))


class Logasun(object):

    def __init__(self, name=None, event_format=None):
        log_file = '%s.log' % name if name else 'yateem.log'
        f = DailyLogFile(log_file, CONST.LOG_DIR)
        observer = FileLogObserver(f, event_format if event_format else self.format_event)
        self.log = Logger(observer=observer)

    def format_event(self, event):
        global time_format
        tz_utc = pytz.timezone('UTC')
        tz_local = pytz.timezone(CONST.LOCAL_TIMEZONE)
        # if isinstance(event['log_time'], basestring):
        #     print '>>>>>>>>>>>>>>>>>>>>>>>>>>>ABOVE MKTIME', event['log_time']
        #     raw_input()
        try:
            event['log_time'] = time.mktime(datetime.datetime.strptime(
                event['log_time'], '%Y-%m-%d %H:%M:%S:%f').timetuple())
        except TypeError:
            pass
            # print 'TypeError'
        except Exception:
            event['log_time'] = time.mktime(
                datetime.datetime.utcnow().timetuple())

        # print '>>>>>>>>>>>>>>>>>>>>>>>>>>>', event['log_time']
        event['log_time'] = datetime.datetime.utcfromtimestamp(
            event['log_time']).replace(tzinfo=tz_utc).astimezone(tz_local)
        event['log_time'] = datetime.datetime.strftime(
            event['log_time'], time_format)

        return u'{log_time} {log_namespace}-{log_level}: {log_format}\n'.format(**{k: repr(v) for k, v in event.items()})
