#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

import sys
import mico.output
from mico.lib.aws.ec2 import *

def ls(*args):
    """List instances filtering with tag name, provided in arguments. Glob
    expressions are allowed in filters as multiple filters too, for
    example::

        mico ec2 ls apaches-* test-*
    """

    for x in ec2_list(*args):
        mico.output.dump(x, layout=env.get("layout","vertical"))

def reboot(*args):
    """Reboot specified instances, for example::

        mico ec2 reboot apaches-* test-*
    """
    for x in ec2_list(*args):
        mico.output.info("Rebooting instance: %s (%s)" % (x.name, x.id,))
        x.reboot()

def main(*args):
    if len(args) > 0:
        fn = getattr(sys.modules[__name__],args[0])
        return fn(*args[1:])
    else:
        return ls()

