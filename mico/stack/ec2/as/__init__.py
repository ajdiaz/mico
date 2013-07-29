#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""The as stack provides function to handle EC2 autoscaling groups.
"""

import sys
import fnmatch
import mico.output
from mico.lib.aws.ec2 import *


__all__ = [ "alarms", "policies" ]


def ls(*args):
    """List autoscaling groups with tag name, provided in arguments. Glob
    expressions are allowed in filters as multiple filters too, for
    example::

        mico ec2.as ls 'host-*' '*database*'
    """

    if args and not args[0]:
        args = ('*',)

    for x in as_list(*args):
        mico.output.dump(x, layout=env.get("layout", "vertical"))


def rm(*args):
    """Remove a number of autoscaling groups which match with specfied glob
    passed as argument. A number of globs are allowed, for example::

        mico ec2.as rm 'host-*', '*database*'
    """
    args = args or ('*',)

    for x in as_list(*args):
        as_delete(x.name, force=True)


def log(*args):
    """Print autoscaling activities log.

    Example::

        mico ec2.as log
    """
    args = args or ('*',)

    for group in as_list(*args):
        for activity in as_activity(group):
            mico.output.dump(activity, layout=env.get("layout", "vertical"))


def instances(*args):
    """List instance which belongs on an specific autoscaling group.
    For example::

        mico ec2.as instances 'apache-*'
    """
    for instance in as_list_instances(*args):
        mico.output.dump(instance, layout=env.get("layout", "vertical"))


def pause(*args):
    """Pause autoscaling group activity. When paused an autoscaling
    group does not grow nor srink
    For example::
        mico ec2.as pause 'apache-*'
    """

    for group in as_list(*args):
        as_pause(group)


def resume(*args):
    """Resume autoscaling group activity.
    For example::
        mico ec2.as resume 'apache-*'
    """

    for group in as_list(*args):
        as_resume(group)


def resize(size, *args):
   """Resize autoscaling group to a specified size.
   When issuing rezie you change AutoScaling Group desired capacity.
   It ignores cooldown time.

   :param size: Desired capacity

   For example::
        mico ec2.as resize 10 'apache-*'
   """
   size = int(size)

   for group in as_list(*args):
        if group.min_size <= size:
            as_resize(group, size)
        else:
            mico.output.error("(%s) desired size %d must be higher than min size %d" %(group.name, size, group.min_size))


def main(*args):
    if len(args) > 0:
        fn = getattr(sys.modules[__name__],args[0])
        return fn(*args[1:])
    else:
        return ls()

