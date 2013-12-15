# -*- coding: utf-8 -*-

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
    elogger = ErosionLogger()
    print elogger.logger
    _app = _make_logging_app(elogger)
    _app.serve(use_debugger=False)
