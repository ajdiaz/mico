#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

import mico.output
from mico.lib.aws.ec2 import *

def instances(*args):
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


def volumes(*args):
    """List volumes filtering with tag name, provided in arguments. Glob
    expressions are allowed in filters as multiple filters too, for
    example::

        volumes('host-*', '*database*')
    """
    fmt = "%(id)-15s%(name)-35s%(status)-15s%(size)-8s" + \
          "%(iops)-6s%(zone)-15s%(device)-20s%(instance_id)-20s"

    print fmt % {
            "id": "ID",
            "name": "Name",
            "status": "Status",
            "size": "Size",
            "iops": "IOPS",
            "zone": "Placement",
            "device": "Device",
            "instance_id": "Instance ID"
    }

    for x in ebs_list(*args):
        print fmt % x


def autoscale(*args):
    """List autoscalign groups filtering with tag name, provided in arguments. Glob
    expressions are allowed in filters as multiple filters too, for
    example::

        autoscale('host-*', '*database*')
    """
    fmt = "%(id)-15s%(name)-20s%(autoscaling_group)-35s%(_state)-15s%(root_device_type)-18s" + \
          "%(instance_type)-12s%(image_id)-20s%(_placement)-15s%(secgroups)-10s%(ip_address)-8s"

    print fmt % {
            "id": "ID",
            "name": "Name",
            "autoscaling_group": "Autoscaling Group",
            "_state": "State",
            "root_device_type": "Root Type",
            "instance_type": "Instance Type",
            "image_id": "Image ID",
            "_placement": "Placement",
            "secgroups": "Groups",
            "ip_address": "IP Address"
    }

    for x in as_list(*args):
        print fmt % x


def main(*args):
    return autoscale(*args)

def main(cmd, *args):
    if cmd == "volumes" or cmd == "vols" or cmd == "vol" or cmd == "v":
        return volumes(*args)
    if cmd == "instances" or cmd == "inst" or cmd == "ins" or cmd == "i":
        return instances(*args)
    if cmd == "autoscaling" or cmd == "autoscale" or cmd == "as":
        return autoscale(*args)

    mico.output.error("invalid command: %s" % cmd)

