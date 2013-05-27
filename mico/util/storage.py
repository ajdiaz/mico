#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""This module provides different ways to store metadata on persistent and
volalile storage."""


import os
import git
import json
import hashlib

from __builtin__ import env


class Storage(dict):
    """Models a basic storage. Just an abstraction, see other implementations
    for real use."""

class FileStorage(Storage):
    """Wrapper to storage in plain JSON files."""

    def __init__(self, path):
        super(FileStorage, self).__init__()
        self.path = path
        try:
            os.makedirs(self.path)
        except OSError:
            # silently pass, do not be afraid :)
            pass

    def __setitem__(self, key, value):
        key = hashlib.sha1(str(key)).hexdigest()
        with open(os.path.join(self.path, key),"w") as f:
            json.dump(value, f)
        self[key] = value

    def __getitem__(self, key):
        key = hashlib.sha1(str(key)).hexdigest()
        if self.get(key,None):
            return self[key]
        else:
            with open(os.path.join(self.path, key),"r") as f:
                 _x = json.load(f)
                 self[key] = _x
                 return _x

class RevisionStorage(Storage):
    """Wrapper to storage which use revision system."""

    REVISION_MESSAGE = "Automatic update: %(filename)s"

    def __init__(self, path):
        """Create a new revision storage with Git backend.

        :type path: str
        :param path: the path to folder where storage will lives.
        """

        super(RevisionStorage, self).__init__()

        self.path = path
        self.repo = git.Repo.init(self.path, mkdir=True)
        writer = self.repo.config_writer()

        # Required in recent versions of git.
        writer.set_value("user", "name", "mico")
        writer.set_value("user", "email", "mico@localhost")

    def __setitem__(self, key, value):
        _path = os.path.join(self.path, os.path.dirname(key).strip("/"))
        try:
            os.makedirs(_path)
        except OSError:
            pass
        _path = os.path.join(self.path, key.strip("/"))
        with open(_path,"w") as f:
            f.write(value)
        self.repo.git.add(_path)
        self.repo.git.commit(
                m=(self.REVISION_MESSAGE % {
                    "filename": _path,
                })
        )


    def __getitem__(self, key):
        with open(os.path.join(self.path, key.strip("/")),"r") as f:
            return f.read()

    def __contains__(self, key):
        return os.path.exists(os.path.join(self.path, key.lstrip("/")))

