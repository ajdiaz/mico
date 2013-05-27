#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""The EIP submodule provide a way to manage Elastic IP resources from
AWS.
"""

import mico.output
from mico.lib.aws.ec2 import ec2_tag
from mico.lib.aws.ec2 import ec2_connect

def eip_allocate(instance=None, force=False):
    """Allocate a new Elastic IP Address.

    :type instance: an instance object
    :param instance: if present check for eip tag in the instance, and try
        to allocate the same address.
    :type force: bool
    :param force: force the ip address resassociation. By default set to
        False.
    """
    if instance is not None:
        if "public_ip" in instance.tags:
            ec2_connect().associate_address(instance, instace.tags["public_ip"])
            mico.output.info("using existent EIP %s for %s" % (
                instace.tags["public_ip"],
                instance)
            )
            return instance.tags["public_ip"]
        else:
            address = ec2_connect().allocate_address().public_ip
            ec2_tag(instance, public_ip = address)
            ec2_connect().associate_address(instance.id, address)
            mico.output.info("created new EIP %s for %s" % (
                address,
                instance.id
            ))
            return address
    else:
        return ec2_connect().allocate_address().public_ip


def eip_exists(public_ip):
    """Return the allocate Elastic IP object which match with public_ip
    passed as argument.
    """
    return ec2_connect().get_all_addresses([public_ip])


def eip_release(public_ip=None, allocation_ip=None):
    """Free up an Elastic IP address.  Pass a public IP address to
    release an EC2 Elastic IP address and an AllocationId to
    release a VPC Elastic IP address.  You should only pass
    one value.

    This requires one of ``public_ip`` or ``allocation_id`` depending
    on if you're associating a VPC address or a plain EC2 address.

    When using an Allocation ID, make sure to pass ``None`` for ``public_ip``
    as EC2 expects a single parameter and if ``public_ip`` is passed boto
    will preference that instead of ``allocation_id``.

    :type public_ip: string
    :param public_ip: The public IP address for EC2 elastic IPs.

    :type allocation_id: string
    :param allocation_id: The Allocation ID for VPC elastic IPs.

    :rtype: bool
    :return: True if successful
    """
    _x = ec2_connect().release_address(public_ip, allocation_id)
    mico.output.info("released EIP: %s" % public_ip)
    return _x


def eip_attach(address, instance):
    """Attach an address to an instance.

    :type address: string
    :param address: the address to be attached
    :type instace: instance object
    :param instance: the instance to be attached to.
    """
    _x = connection.associate_address(instance.id, address)
    mico.output.info("attached EIP %s to %s" % (
        address,
        instance.id
    ))
    return _x

eip_ensure = eip_allocate
eip_delete = eip_release

