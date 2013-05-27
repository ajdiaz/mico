#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

class AttrDict(dict):
    """Wrapper dictionary which allows to access items using getattr."""

    def __getattr__(self, item):
        if item[0] == "_":
            return getattr(super(AttrDict, self), item)
        else:
            return self[item]

    def __setattr__(self, item, value):
        if item[0] == "_":
            setattr(super(AttrDict, self), item, value)
        else:
            self[item] = value


class AttrLazyDict(AttrDict):
    """Wrapper dictionary which allows to access items using getattr and
    return None if value do not exists yet."""

    def __getattr__(self, item):
        try:
            return getattr(super(AttrDict, self), item)
        except KeyError:
            return None


class AutoCreatedDict(dict):
    """Wrapper for dictionary which create values when reading

    :type cached: bool
    :param cached: When set to True (by default), the value for a field will
        be cached in memory for future acceses, so this value will be never
        update.
    """
    def __init__(self, data={}, cached=True):
        self._cached = cached
        self._cache = AttrLazyDict(data)

    def __setitem__(self, key, value):
        super(AutoCreatedDict, self).__setitem__(key, value)

    def __getitem__(self, key):
        if self._cache.get(key, None) is not None:
            return self._cache[key]
        else:
            fn = super(AutoCreatedDict, self).__getitem__(key)
            if self._cached:
                self._cache[key] = fn()
                return self._cache[key]
            else:
                return fn()

class AutoCreatedLazyDict(object):
    """Mixin to merge AttrLazyDict and LazyDict."""
    def __init__(self, data):
        self.d = AutoCreatedDict(data)

    def __getitem__(self, key):
        return self.d[key]

    def __setitem__(self, key, value):
        self.d[key] = value

    def __getattr__(self, attr):
        if attr != "d":
            return self.d[attr]
        else:
            return self.d

    def __repr__(self):
        return repr(self.d)




