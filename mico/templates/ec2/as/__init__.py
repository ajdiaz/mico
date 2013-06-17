#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

import sys
import fnmatch
import mico.output
from mico.lib.aws.ec2 import *

def ls(*args):
    """List autoscaling groups with tag name, provided in arguments. Glob
    expressions are allowed in filters as multiple filters too, for
    example::

        ls('host-*', '*database*')
    """

    if args and not args[0]:
        args = ('*',)

    for x in as_list(*args):
        mico.output.dump(x, layout=env.get("layout", "vertical"))

def rm(*args):
    """Remove a number of autoscaling groups which match with specfied glob
    passed as argument. A number of globs are allowed, for example::

        rm('host-*', '*database*')
    """
    args = args or ('*',)

    for x in as_list(*args):
        as_delete(x.name, force=True)

def log(*args):
    """Print autoscaling activities log.
    """
    args = args or ('*',)

    for group in as_list(*args):
        for activity in as_activity(group):
            mico.output.dump(activity, layout=env.get("layout", "vertical"))


from alarms import ls as alarms
from alarms import rm as rm_alarms
from policies import ls as policies

def main(*args):
    if len(args) > 0:
        fn = getattr(sys.modules[__name__],args[0])
        return fn(*args[1:])
    else:
        return ls()

