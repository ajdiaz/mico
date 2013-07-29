#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""The alarms stack provides function to handle alarms related with EC2
autoscaling groups.
"""

import sys
import fnmatch

import mico.output
from mico.lib.aws.ec2 import *


def ls(*args):
    """List alarms defined for autoscaling groups, searching for alarm name
    (not autoscaling group name). For example::

        mico ec2.as.alarms ls 'my-alarm-*'
    """
    args = args or ('*',)

    for alarm in as_list_alarms(*args):
        mico.output.dump(alarm, layout=env.get("layout", "vertical"))


def rm(*args):
    """Remove alarms created with an autoscaling group, searching for alarm
    name (not autoscaling group name). For example::

        mico ec2.as.alarms rm 'my-alarm-*'
    """
    for arg in args:
        as_delete_alarm(arg)


def main(*args):
    if len(args) > 0:
        fn = getattr(sys.modules[__name__],args[0])
        return fn(*args[1:])
    else:
        return ls()

