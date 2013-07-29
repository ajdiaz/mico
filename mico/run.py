#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

import fabric.api
from fabric.tasks import execute as fabric_execute

import mico.hook

from mico.lib.core.sudo import is_sudo
from mico.lib.core.local import is_local, run_local


class ExecutionError(Exception):
    """Models an execution error"""


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



