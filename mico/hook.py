#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""Hooks are useful toy for fabric. Current versions of fabric do not
support post action hooks."""

import traceback
from functools import wraps

import mico
import mico.output

from __builtin__ import env

# global variable for add_hooks()
parent_task_name = ''

def task_add_post_run_hook(hook, *args, **kwargs):
    '''Run hook after Fabric tasks have completed on all hosts

    Example usage:
        @add_post_run_hook(postrunfunc, 'arg1', 'arg2')
        def mytask():
            # ...

    '''
    def true_decorator(f):
        return add_hooks(post=hook, post_args=args, post_kwargs=kwargs)(f)
    return true_decorator


def task_add_pre_run_hook(hook, *args, **kwargs):
    '''Run hook before Fabric tasks have completed on all hosts

    Example usage:
        @add_pre_run_hook(prerunfunc, 'arg1', 'arg2')
        def mytask():
            # ...

    '''
    def true_decorator(f):
        return add_hooks(pre=hook, pre_args=args, pre_kwargs=kwargs)(f)
    return true_decorator


def add_hooks(pre=None, pre_args=(), pre_kwargs={},
              post=None, post_args=(), post_kwargs={}):
    '''
    Function decorator to be used with Fabric tasks.  Adds pre-run
    and/or post-run hooks to a Fabric task.  Uses env.all_hosts to
    determine when to run the post hook.  Uses the global variable,
    parent_task_name, to check if the task is a subtask (i.e. a
    decorated task called by another decorated task). If it is a
    subtask, do not perform pre or post processing.

    pre: callable to be run before starting Fabric tasks
    pre_args: a tuple of arguments to be passed to "pre"
    pre_kwargs: a dict of keyword arguments to be passed to "pre"
    post: callable to be run after Fabric tasks have completed on all hosts
    post_args: a tuple of arguments to be passed to "post"
    post_kwargs: a dict of keyword arguments to be passed to "post"

    '''
    # create a namespace to save state across hosts and tasks
    class NS(object):
        run_counter = 0

    def true_decorator(f):
        @wraps(f)
        def f_wrapper(*args, **kwargs):
            # set state variables
            global parent_task_name
            if not parent_task_name:
                parent_task_name = f.__name__
            NS.run_counter += 1

            # pre-run processing
            if f.__name__ == parent_task_name and NS.run_counter == 1:
                if pre:
                    pre(*pre_args, **pre_kwargs)

            # run the task
            r = None
            try:
                r = f(*args, **kwargs)
            except SystemExit:
                pass
            except mico.ExecutionError as e:
                mico.output.error(str(e))
            except:
                raise

            # post-run processing
            if (f.__name__ == parent_task_name and
                NS.run_counter >= len(env.all_hosts)):
                if post:
                    post(*post_args, **post_kwargs)

            return r
        return f_wrapper
    return true_decorator


from Queue import Queue

def add_hook(context, action, parameters=()):
    """Enqueue one action with action parameters in environment"""

    if context in env:
        env[context].put((action,parameters))
    else:
        env[context] = Queue()
        env[context].put((action,parameters))

def add_pre_hook(action, parameters=()):
    return add_hook("pre_hook", action, parameters)

def add_post_hook(action, parameters=()):
    return add_hook("post_hook", action, parameters)

def run_hook(context):
    if context in env:
        run = set()
        ret = []
        q = env[context]
        while not q.empty():
            action, parameters = q.get()
            if (action, parameters) in run:
                ## TODO: log skip running
                continue
            else:
                ret.append(action(*parameters))
        return ret
    else:
        return []

def run_pre_hook():
    return run_hook("pre_hook")

def run_post_hook():
    return run_hook("post_hook")

