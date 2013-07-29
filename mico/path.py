#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

import os
import sys


def get_stack_path(env_var="MICO_STACK_PATH", path=[]):
    """Set the stack path for mico. By default use the following directories
    (in order):

    1. The current working directory (highest precedence)
    2. The ~/.config/mico directory
    3. Global /etc/mico directory
    4. Local "stack" directory in mico source code (lowest precedence)

    :type env_var: str
    :param env_var: the OS environment variable name which content will be
        prepended as stack path.

    :type path: list
    :param path: a number of paths (strings) to be appended to stack path.
    """
    _path = [
        os.curdir,
        os.path.join(os.environ.get("HOME","/"), ".config/mico"),
        "/etc/mico",
        os.path.join(os.path.dirname(__file__), "stack"),
    ]

    if os.environ.get(env_var, None):
       _path.insert(0, os.environ.get(env_var))

    if path:
        _path.extend(path)

    return _path


def get_cache_path(env_var="MICO_CACHE_PATH"):
    return os.environ.get("MICO_CACHE_PATH", None) or \
           os.path.join(os.environ.get("HOME","/"), ".cache/mico")


def get_library_path(env_var="MICO_LIBRARY_PATH", path=[]):
    """Set the library path for mico. By default use the following directories
    (in order):

    1. ~/.local/share/mico directory
    2. /usr/lib/mico
    3. /usr/local/lib/mico
    4. /usr/share/mico
    5. /usr/local/share/mico

    :type env_var: str
    :param env_var: the OS environment variable name which content will be
        prepended as library path.

    :type path: list
    :param path: a number of paths (strings) to be appended to library path.
    """
    _path = [
        os.curdir,
        os.path.join(os.environ.get("HOME","/"), ".local/share/mico"),
        "/usr/lib/mico",
        "/usr/local/lib/mico",
        "/usr/share/mico",
        "/usr/local/share/mico",
    ]

    if os.environ.get(env_var, None):
       _path.insert(0, os.environ.get(env_var))

    if path:
        _path.extend(path)

    return _path

