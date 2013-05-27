#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

from threading import Lock

class Mutex(object):
    _current_mutex = {}

    def __init__(self, name):
        self._lock = Lock()
        self.name = name

    @classmethod
    def get_mutex(cls, name="_default"):
        if name not in Mutex._current_mutex:
            Mutex._current_mutex[name] = Mutex(name)

        return Mutex._current_mutex[name]

    def __del__(self):
        Lock.__del__(self)
        if self.name in Mutex._current_mutex:
            del Mutex._current_mutex[self.name]

    def __enter__(self):
        return self._lock.__enter__()

    def __exit__(self, typ, value, traceback):
        return self._lock.__exit__()


