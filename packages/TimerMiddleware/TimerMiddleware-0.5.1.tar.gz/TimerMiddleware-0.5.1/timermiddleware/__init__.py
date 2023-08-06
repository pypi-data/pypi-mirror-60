from __future__ import with_statement

from __future__ import absolute_import
from __future__ import unicode_literals
import datetime
import json
import logging
import threading

from random import random
from time import time
from contextlib import contextmanager

from webob import Request
import six

# Actually import time, but close enough to
# wsgi process start time to use as such
PROCESS_START_TIME = datetime.datetime.utcnow()

log = logging.getLogger(__name__)


def uptime():
    """Return process uptime (in seconds) for this wsgi app."""
    td = datetime.datetime.utcnow() - PROCESS_START_TIME
    return (td.days * 3600 * 24) + td.seconds


class StatsRecord(object):
    def __init__(self, request):
        self._custom_stats = {}
        self.timers = {}
        self.counts = {}
        self.url = six.ensure_text(request.environ['PATH_INFO'])
        if request.environ['QUERY_STRING']:
            self.url += '?' + six.ensure_text(request.environ['QUERY_STRING'])
        self.request = request
        # Avoid double-timing things
        self._now_timing = set()

    def add(self, k, v):
        self._custom_stats[k] = v

    def remove(self, k):
        if k in self._custom_stats:
            del self._custom_stats[k]

    def __repr__(self):
        stats = dict(
            url=self.url,
            uptime=uptime(),
            timings=dict((k, int(v * 1000))
                         for k, v in six.iteritems(self.timers)),
            call_counts=dict(self.counts),
        )
        stats.update(self._custom_stats)
        return self.to_string(stats)

    def to_string(self, stats):
        return json.dumps(stats)

    @contextmanager
    def timing(self, name):
        if name not in self._now_timing:
            self._now_timing.add(name)
            self.timers.setdefault(name, 0)
            self.counts.setdefault(name, 0)
            begin = time()
            try:
                yield True
            finally:
                end = time()
                self.timers[name] += end-begin
                self.counts[name] += 1
                self._now_timing.remove(name)
        else:
            yield False


class Timer(object):
    '''Decorator to time a method call'''
    def __init__(self, timer_name, target_class, *names, **kw):
        self.timer_name = timer_name
        self.target_class = target_class
        self.names = self.get_names(names)
        self.debug_each_call = kw.get('debug_each_call', True)

    def get_names(self, names):
        if '*' not in names:
            return names
        import inspect
        return [meth[0] for meth in inspect.getmembers(self.target_class,
            predicate=inspect.ismethod)]

    def decorate(self, middleware):
        for name in self.names:
            setattr(self.target_class, name,
                    TimingDecorator(getattr(self.target_class, name),
                                    self.timer_name,
                                    name,
                                    self.debug_each_call,
                                    middleware))


class TimingDecorator(object):
    def __init__(self, inner, timer_name, method_name, debug_each_call, middleware):
        self._inner = inner
        self.timer_name = timer_name
        self.method_name = method_name
        self.debug_each_call = debug_each_call and \
                               log.isEnabledFor(logging.DEBUG)
        self.middleware = middleware
        self.debug_line_length = int(middleware.config.get('stats.debug_line_length', 100))

    def __get__(self, inst, cls=None):
        func = self._inner.__get__(inst, cls)

        def wrapper(*args, **kwargs):
            return self.run_and_log(func, inst, *args, **kwargs)
        return wrapper

    def __call__(self, *args, **kwargs):
        return self.run_and_log(self._inner, None, *args, **kwargs)

    def run_and_log(self, func, instance, *args, **kwargs):
        stats = self.middleware.stat_record
        if not stats:
            return func(*args, **kwargs)

        timer_name = self.timer_name.format(
            method_name=self.method_name,
            instance=instance,
        )
        with stats.timing(timer_name) as timed_this_one:
            call_method = '%s call: ' % timer_name
            if instance is not None:
                call_method += str(type(instance))
            call_method += ' ' + self.method_name
            call_args = ' args=%s kwargs=%s' % (six.ensure_text(repr(args)),
                                                six.ensure_text(repr(kwargs)))
            if len(call_args) > self.debug_line_length:
                call_args = call_args[:self.debug_line_length] + '...'

            output = call_method+call_args
            if self.debug_each_call and timed_this_one:
                log.debug(output)

            if timed_this_one:
                self.middleware.dispatch(output)

            retval = func(*args, **kwargs)
            if timed_this_one and type(retval).__name__ == 'generator':
                return GeneratorTimingProxy(retval, timer_name, stats, self.debug_each_call)
            return retval


class GeneratorTimingProxy(object):
    def __init__(self, generator, timer_name, stats, debug_each_call):
        self.generator = generator
        self.timer_name = timer_name
        self.stats = stats
        self.debug_each_call = debug_each_call

    def __iter__(self):
        return self

    def next(self):
        with self.stats.timing(self.timer_name+'.next') as timed_this_one:
            if self.debug_each_call and timed_this_one:
                log.debug('%s.next call', self.timer_name)
            return next(self.generator)
    __next__ = next

    def __getattr__(self, name):
        return getattr(self.generator, name)


class TimerMiddleware(object):
    LISTENERS = []
    stat_record_class = StatsRecord

    def __init__(self, app, config):
        self.app = app
        self.config = config
        self.log = logging.getLogger('stats')
        self.sample_rate = float(self.config.get('stats.sample_rate', 0))
        self.tl = threading.local()
        if self.sample_rate:
            for t in self.timers():
                t.decorate(self)

    @property
    def stat_record(self):
        return getattr(self.tl, 'stat_record', None)

    @stat_record.setter
    def stat_record(self, value):
        self.tl.stat_record = value

    @classmethod
    def register_listener(cls, listener):
        """Registers a listener for TimerMiddleware.
        This is listener will be called for everytimed method.
        It does not honor debug_each_call.
        """
        cls.LISTENERS.append(listener)

    @classmethod
    def unregister_listener(cls, listener):
        cls.LISTENERS.remove(listener)

    @classmethod
    def dispatch(cls, output):
        """Send the output to all of the registered listeners"""
        for listener in TimerMiddleware.LISTENERS:
            listener(output)

    def __call__(self, environ, start_response):
        req = Request(environ)
        active = random() < self.sample_rate

        if active:
            self.stat_record = s = self.stat_record_class(req)
            with s.timing('total'):
                resp = req.get_response(self.app)
                result = resp(environ, start_response)
                s = self.before_logging(s)
            self.log.info('%r', s)
            self.stat_record = None
        else:
            resp = req.get_response(self.app)
            result = resp(environ, start_response)

        return result

    def before_logging(self, stat_record):
        """Called right before the timing results are logged. Override in a
        sublass if you want to modify the stat_record before it's logged.
        """
        return stat_record

    def timers(self):
        """Return a list of :class:`Timer` objects. Override in a subclass."""
        return []
