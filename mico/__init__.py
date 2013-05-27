#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

import os
import sys

# Set the configuration PATH
config_path = [
        os.curdir,
        os.path.join(os.environ.get("HOME","/"), ".config/mico"),
        "/etc/mico",
        os.path.join(os.path.dirname(__file__), "templates"),
        os.path.join(os.curdir, "files")
]

if os.environ.get("MICO_CONFIG_PATH", None):
    config_path.insert(0, os.environ.get("MICO_CONFIG_PATH"))

# Set the cache PATH
cache_path = os.environ.get("MICO_CACHE_PATH", None) or \
             os.path.join(os.environ.get("HOME","/"), ".cache/mico")

# Set the lib PATH
lib_path = [
        os.path.join(os.environ.get("HOME","/"), ".local/share/mico"),
        "/usr/lib/mico",
        "/usr/local/lib/mico",
        "/usr/share/mico"
        "/usr/local/share/mico"
]

if os.environ.get("MICO_LIBRARY_PATH", None):
    lib_path.insert(0, os.environ.get("MICO_LIBRARY_PATH"))

sys.path.extend(lib_path)
sys.path.extend(config_path)

import __builtin__
from mico.util.dicts import AutoCreatedLazyDict
from fabric.api import env

__builtin__.env = env
__builtin__.env.custom = AutoCreatedLazyDict(env)

import mico.environ

import mico.hook
from fabric.tasks import execute as fabric_execute

def execute(action, *args, **kwargs):
    """Exec allows you to execute an action using fabric API, adding pre-hook
    and post-hook into the pipeline if required."""

    return fabric_execute(
             mico.hook.task_add_pre_run_hook( mico.hook.run_pre_hook )
                ( mico.hook.task_add_post_run_hook( mico.hook.run_post_hook )
                    ( action )), *args, **kwargs )

import fabric.api
from mico.lib.core.sudo import is_sudo
from mico.lib.core.local import is_local, run_local

def run(*args, **kwargs):
    """A wrapper to Fabric's run/sudo commands that takes into account
    the mode_local.
    """
    if "force" in kwargs:
        force = kwargs["force"]
        del kwargs["force"]
    else:
        force = False

    if is_local():
        if is_sudo():
            kwargs.setdefault("sudo", True)
        _exe = run_local(*args, **kwargs)
    else:
        mico.output.debug(" ".join(args))
        if is_sudo():
            _exe = fabric.api.sudo(*args, **kwargs)
        else:
            _exe = fabric.api.run(*args, **kwargs)

    if _exe.return_code != 0 and not force:
        raise ExecutionError("%s: failed to run '%s' (retcode:%d): '%s'" % (
            env.host_string,
            " ".join(args),
            _exe.return_code,
            str(_exe)
        ))
    else:
        return _exe

class ExecutionError(Exception):
    """Models an execution error"""

__builtin__.run_local = run_local
__builtin__.run = run


from mico.decorators import async, serial, parallel, sync
__builtin__.async = async
__builtin__.serial = serial
__builtin__.parallel = parallel
__builtin__.sync = sync

from mico.util.storage import FileStorage
__builtin__.env.storage = FileStorage(cache_path)

def save(key, data):
    "Save a data in the global cache catalog."
    env.storage[key] = data

def load(key):
    "Get a data saved in global cache catalog."
    return env.storage[key]

