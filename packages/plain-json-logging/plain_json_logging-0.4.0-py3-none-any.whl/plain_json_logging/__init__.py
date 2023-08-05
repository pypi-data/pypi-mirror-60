import collections
import datetime
import json
import pytz
import sys

class PlainJsonLogging:

    def __init__(self,
      file=sys.stderr,
      strftime='%Y-%m-%dT%H:%M:%S.%f',
      timezone=None,
      timedelta=0,
      timestampname='timestamp',
      messagename='message',
      levelname='level',
      levelinfo='INFO',
      levelwarn='WARN',
      levelerror='ERROR',
      constextra=None):
        self.file = file
        self.time = {
            'strftime': strftime,
            'tz': pytz.utc if timezone is None else pytz.timezone(timezone),
            'timedelta': datetime.timedelta(minutes=timedelta),
        }
        self.name = {
            'timestamp': timestampname,
            'message': messagename,
            'level': levelname,
        }
        self.level = {
            'info': levelinfo,
            'warn': levelwarn,
            'error': levelerror,
        }
        self.constextra = constextra

    def __timestamp(self):
        now = datetime.datetime.now(tz=self.time['tz']) + self.time['timedelta']
        return now.strftime(self.time['strftime'])

    def __dump(self, log):
        self.file.write(json.dumps(log, ensure_ascii=False) + u'\n')

    def __log(self, level, message, extra=None):
        log = collections.OrderedDict()
        log[self.name['timestamp']] = self.__timestamp()
        log[self.name['level']] = level
        log[self.name['message']] = message
        if self.constextra is not None:
            for key in self.constextra.keys():
                log[key] = self.constextra[key]
        if extra is not None:
            for key in sorted(extra.keys()):
                log[key] = extra[key]
        self.__dump(log)

    def info(self, message, extra=None):
        self.__log(self.level['info'], message, extra)
        return self

    def warn(self, message, extra=None):
        self.__log(self.level['warn'], message, extra)
        return self

    def error(self, message, extra=None):
        self.__log(self.level['error'], message, extra)
        return self