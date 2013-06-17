#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

import sys
import fnmatch
import mico.output
from mico.lib.aws.ec2 import *

def ls(*args):
    """List policies.
    """
    args = args or ('*',)

    for policy in as_list_policies(*args):
        mico.output.dump(policy, layout=env.get("layout", "vertical"))


def main(*args):
    if len(args) > 0:
        fn = getattr(sys.modules[__name__],args[0])
        return fn(*args[1:])
    else:
        return ls()

