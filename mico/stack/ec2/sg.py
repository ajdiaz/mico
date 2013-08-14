#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""SG stack provides functions to work with AWS EC2 Security Groups.
"""

import sys
import mico.output
from mico.lib.aws.ec2 import *

def rm(*args):
    """Removes the security groups that matches with the security group name passed as argument.

        mico ec2.sg rm sg01 sg02

    If the security group is referenced by another security group, you need to set the *force*
    variable to True in order to delete the rules before.
    """
    for x in args:
        _x = sg_delete(x,env.get("force", False))
        mico.output.info("Removed security group %s" % (_x.name,))

def main(*args):
    if len(args) > 0:
        fn = getattr(sys.modules[__name__],args[0])
        return fn(*args[1:])
    else:
        return ls()
