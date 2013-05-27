#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

class Switcher(object):
    """Switch a global status using the environment as critical region, and
    setted using class constructor.
    """

    _switch = (None, None)

    def __init__(self, init_value = None):
        self._old_value = env.get(self._switch[0], None)
        env[self._switch[0]] = self._switch[1]  \
                               if init_value is None \
                               else init_value

    def __enter__(self):
        pass

    def __exit__(self, t, v, tr):
        if self._old_value is None:
            del env[self._switch[0]]
        else:
            env[self._switch[0]] = self._old_value

    @staticmethod
    def getValue(key):
        return env.get(key, None)

    @classmethod
    def from_key(cls, key, value):
        return type.__new__(type,"switch_%s" % key, (Switcher,),{ "_switch": (key, value) })


