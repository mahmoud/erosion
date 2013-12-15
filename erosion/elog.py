# -*- coding: utf-8 -*-
import time
import common

from clastic import Middleware
from lithoxyl import (DEBUG,
                      BaseLogger,
                      SensibleSink,
                      StructuredFileSink,
                      StreamEmitter,
                      Formatter)


class BasicErosionLogger(Middleware):
    provides = ('log_record',)

    def __init__(self, filename=None):
        self.file_sink = StructuredFileSink()
        self.target_level = DEBUG
        self.logger = BaseLogger('erosion', [self.file_sink])

    def request(self, next):
        with self.logger.record('request', self.target_level) as r:
            return next(log_record=r)


class ErosionHTTPLogger(Middleware):
    """"\
    A toy logger middleware that attempts to mimic the log output
    of the wsgiref server, which is somewhat close to the "standard"
    http log format
    """
    _monthnames = [None,
                   'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    provides = ('http_log_record',)
    format_str = ('{remote_addr} - - [{http_date}]'
                  ' "{http_method} {http_path} {http_protocol}"'
                  ' {http_status} -')

    def __init__(self, filename=None):
        self.formatter = Formatter(self.format_str)
        self.emitter = StreamEmitter('stdout')

        self.sink = SensibleSink(formatter=self.formatter,
                                 emitter=self.emitter)
        self.target_level = DEBUG
        self.logger = BaseLogger('erosion', [self.sink])

    def request(self, next, request):
        with self.logger.record('request', self.target_level) as r:
            r['remote_addr'] = request.remote_addr
            r['http_date'] = self.current_time_formatted()
            r['http_method'] = request.method
            r['http_path'] = request.path
            r['http_protocol'] = request.environ['SERVER_PROTOCOL']
            try:
                ret = next(http_log_record=r)
            except Exception as exc:
                # this is the reason why http logging here is just a toy.
                # later middlewares (and clastic) can change the status code
                # to something other than 500 in the event of a
                # non-HTTPException error
                r['http_status'] = getattr(exc, 'status_code', 500)
                raise
            else:
                r['http_status'] = getattr(ret, 'status_code', None)
            return ret

    def current_time_formatted(self):
        now = time.time()
        year, month, day, hh, mm, ss, x, y, z = time.localtime(now)
        s = "%02d/%3s/%04d %02d:%02d:%02d" % (day,
                                              self._monthnames[month],
                                              year, hh, mm, ss)
        return s


class ErosionLogger(Middleware):
    default_format_str = '{logger_name}: {record_status} {duration_msecs}'
    provides = ('log_record',)

    def __init__(self, filename=None):
        self.formatter = Formatter(self.default_format_str)
        self.emitter = StreamEmitter('stdout')

        self.sink = SensibleSink(formatter=self.formatter,
                                 emitter=self.emitter)
        self.target_level = DEBUG
        self.logger = BaseLogger('erosion', [self.sink])

    def request(self, next):
        with self.logger.record('request', self.target_level) as r:
            return next(log_record=r)


def _make_logging_app(logger):
    from clastic import Application, render_basic

    def _test_ep(counter):
        counter['count'] += 1
        if counter['count'] % 2 == 0:
            raise ValueError('errors are one form of success')
        return 'yay %r' % counter

    _app = Application([('/', _test_ep, render_basic)],
                       resources={'counter': {'count': 0}},
                       middlewares=[logger])
    return _app


if __name__ == '__main__':
    elogger = ErosionHTTPLogger()
    print elogger.logger
    _app = _make_logging_app(elogger)
    _app.serve(use_debugger=False)
