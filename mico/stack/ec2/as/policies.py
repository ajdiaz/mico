#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""The policies stack provides functions to handle EC2 autoscaling groups
policies.
"""

import sys
import mico.output
from mico.lib.aws.ec2 import *


def ls(*args):
    """List scaling policies associated with autoscaling group. Searching
    for policy name (not autoscaling group name). For example::

        mico ec2.as.policies ls 'pol-*'
    """
    args = args or ('*',)

    for policy in as_list_policies(*args):
        mico.output.dump(policy, layout=env.get("layout", "vertical"))


def main(*args):
    if len(args) > 0:
        fn = getattr(sys.modules[__name__], args[0])
        return fn(*args[1:])
    else:
        return ls()

