#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

from threading import Thread
from functools import wraps

from fabric.api import parallel as fabric_parallel
from mico.util.mutex import Mutex

parallel = fabric_parallel


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
        func_th = Thread(target = func, args = args, kwargs = kwargs)
        func_th.start()
        return func_th

    return _inner

def serial(func):
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

        @serial
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


def sync(f):
    """Decorator to synchronize a function while running in asynchronous
    mode. Let's suppose that you have a number of tasks decorated by
    ``@async``, but you need to ensure that one common action is
    synchronized over all of them, then ``@sync`` is for you.

    .. note:: The ``@sync`` decorator is radically different of ``@serial``.
        While ``@serial`` waits for every thread to be done, ``@sync`` just only
        ensure that the decorated function is calling once a time.
    """
    def _f(*args, **kw):
        with Mutex.get_mutex(f.__name__):
            return f(*args, **kw)
    return _f

