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

        instances('host-*', '*database*')
    """

    fmt = "%(id)-15s%(name)-32s%(_state)-15s%(root_device_type)-15s" + \
          "%(instance_type)-12s%(image_id)-20s%(_placement)-15s%(secgroups)-25s%(ip_address)-20s"

    print fmt % {
            "id": "ID",
            "name": "Name",
            "_state": "State",
            "root_device_type": "Root Type",
            "instance_type": "Instance Type",
            "image_id": "Image ID",
            "_placement": "Placement",
            "secgroups": "Groups",
            "ip_address": "IP Address"
    }

    for x in ec2_list(*args):
        print fmt % x

def main(*args):
    if len(args) > 0:
        fn = getattr(sys.modules[__name__],args[0])
        return fn(args[1:])
    else:
        return ls()

