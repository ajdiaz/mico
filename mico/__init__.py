#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

import os
import sys

import mico.path

# Set the cache PATH
cache_path = os.environ.get("MICO_CACHE_PATH", None) or \
             os.path.join(os.environ.get("HOME","/"), ".cache/mico")

sys.path.extend(mico.path.get_library_path())

import __builtin__
from mico.util.dicts import AutoCreatedLazyDict
from fabric.api import env

__builtin__.env = env
__builtin__.env.custom = AutoCreatedLazyDict(env)

import mico.environ

import mico.hook
from fabric.tasks import execute as fabric_execute

from functools import partial

def execute(action, output, *args, **kwargs):
    """Exec allows you to execute an action using fabric API, adding pre-hook
    and post-hook into the pipeline if required."""

    if output:
        def run(*args, **kwargs):
            mico.output.debug(" ".join(args))
            return mico.output.info(action(*args, **kwargs))
    else:
        def run(*args, **kwargs):
            return action(*args, **kwargs)

    return fabric_execute(
             mico.hook.task_add_pre_run_hook( mico.hook.run_pre_hook )
                ( mico.hook.task_add_post_run_hook( mico.hook.run_post_hook )
                    ( run )), *args, **kwargs )

import fabric.api
from mico.lib.core.sudo import is_sudo
from mico.lib.core.local import is_local, run_local

def run(*args, **kwargs):
    """A wrapper to Fabric's run/sudo commands that takes into account
    the mode_local.
    """
    ret = []
    if "force" in kwargs:
        force = kwargs["force"]
        del kwargs["force"]
    else:
        force = False

    if is_local():
        if is_sudo():
            kwargs.setdefault("sudo", True)
        _exes = execute(run_local, True, *args, **kwargs)
    else:
        if is_sudo():
            _exes = execute(fabric.api.sudo, True, *args, **kwargs)
        else:
            _exes = execute(fabric.api.run, True, *args, **kwargs)

    for k, _exe in _exes.items():
        if _exe.return_code != 0 and not force:
            raise ExecutionError("%s: failed to run '%s' (retcode:%d): '%s'" % (
                env.host_string,
                " ".join(args),
                _exe.return_code,
                str(_exe)
         ))
        else:
            ret.append(_exe)
    return ret

class ExecutionError(Exception):
    """Models an execution error"""

__builtin__.run_local = run_local
__builtin__.run = run
__builtin__.execute = execute


from mico.decorators import async, serial, parallel, sync, lock
__builtin__.async = async
__builtin__.serial = serial
__builtin__.parallel = parallel
__builtin__.sync = sync
__builtin__.lock = lock

from mico.util.storage import FileStorage
__builtin__.env.storage = FileStorage(cache_path)

def save(key, data):
    "Save a data in the global cache catalog."
    env.storage[key] = data

def load(key):
    "Get a data saved in global cache catalog."
    return env.storage[key]

