#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

from threading import Thread
from functools import wraps

from fabric.api import parallel as fabric_parallel
from fabric.api import serial as fabric_serial
from mico.util.mutex import Mutex

import mico.output


parallel = fabric_parallel
serial = fabric_serial


def async(func):
    """Function decorator, intended to make "func" run in a separate
    thread  (asynchronously).

    Example:

    .. code-block:: python

        @async
        def task1():
            do_something

        @async
        def task2():
            do_something_too

        t1 = task1()
        t2 = task2()

        t1.join()
        t2.join()
	"""

    @wraps(func)
    def _inner(*args, **kwargs):
        if env.parallel:
            func_th = Thread(target = func, args = args, kwargs = kwargs)
            func_th.start()
            return func_th
        else:
            mico.output.debug("Avoid async action for %s due to env.parallel = False" % func.__name__)
            return func(*args, **kwargs)

    return _inner


def sync(func):
    """Function decorator, intended to make "func" wait for threading async
    finished.

    Example:

    .. code-block:: python

        @async
        def task1():
            do_something

        @async
        def task2():
            do_something_too

        @sync
        def task3():
            do_something_when_task1_and_task2_finished()

        t1 = task1()
        t2 = task2()
        t3 = task3() # Only runs when task1 and task2 finished.
    """

    @wraps(func)
    def _inner(*args, **kwargs):
        import threading, time
        while threading.activeCount() > 1:
            time.sleep(1)
        return func(*args, **kwargs)
    return _inner


def lock(f):
    """Decorator to synchronize a function while running in asynchronous
    mode. Let's suppose that you have a number of tasks decorated by
    ``@async``, but you need to ensure that one common action is
    synchronized over all of them, then ``@lock`` is for you.

    .. note:: The ``@lock`` decorator is radically different of ``@sync``.
        While ``@sync`` waits for every thread to be done, ``@lock`` just only
        ensure that the decorated function is calling once a time.

    Example::

        @lock
        def task():
            # access to critical region
    """
    def _f(*args, **kw):
        with Mutex.get_mutex(f.__name__):
            return f(*args, **kw)
    return _f


def environ(name):
    """Decorator to set new environment variables. Using this decoration you
    can create environment dynamic properties, for example, you can set new
    one environ called 'uptime' which contains the remote system uptime
    using the core stack function 'uptime'::

        @environ('uptime')
        def _env_uptime():
            return mico.lib.core.uptime()

    Then you can use the new custom environ in the form::

        print env.custom.uptime

    Or in the old and good dictionary style::

        print env.custom["uptime"]

    """

    def _decorator(fn):
        setattr(sys.modules[__name__], name, fn)
        mico.env.custom[name] = fn
    return _decorator


