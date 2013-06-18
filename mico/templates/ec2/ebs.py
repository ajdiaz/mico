#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

import sys
import mico.output
from mico.lib.aws.ec2 import *

def ls(*args):
    """List volumes filtering with tag name, provided in arguments. Glob
    expressions are allowed in filters as multiple filters too, for
    example::

        mico ec2.ebs ls apaches-* test-*
    """
    for x in ebs_list(*args):
        mico.output.dump(x, layout=env.get("layout","vertical"))

def main(*args):
    if len(args) > 0:
        fn = getattr(sys.modules[__name__],args[0])
        return fn(*args[1:])
    else:
        return ls()

