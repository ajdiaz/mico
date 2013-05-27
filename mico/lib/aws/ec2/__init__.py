#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""The EC2 template provide a number of subtemplates to handle EC2 cloud
resources, like instance, volumes and so on.

Example of usage in host definitions::

    from mico.lib.aws.ec2 import *
    ec2_run('ami-12345')
"""

import time
import itertools
from os import environ as os_environ
from fnmatch import fnmatch

from boto.ec2 import get_region
from boto.ec2.connection import EC2Connection

import mico.output

class EC2TemplateError(Exception):
    """Model an exception related with EC2 API."""


def ec2_connect(region=None):
    """Helper to connect to Amazon Web Services EC2, using identify provided
    by environment, as also optional region in arguments.
    """
    if not os_environ.get("AWS_ACCESS_KEY_ID", None):
        raise EC2TemplateError("Environment variable AWS_ACCESS_KEY_ID is not set.")
    if not os_environ.get("AWS_SECRET_ACCESS_KEY", None):
        raise EC2TemplateError("Environment variable AWS_SECRET_ACCESS_KEY is not set.")

    if not region:
        region = env.get("ec2_region")

    region = get_region(region,
            aws_access_key_id = os_environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key = os_environ.get("AWS_ACCESS_SECRET_KEY")
    )

    connection = EC2Connection(
            os_environ.get("AWS_ACCESS_KEY_ID"),
            os_environ.get("AWS_SECRET_ACCESS_KEY"),
            region = region
    )

    return connection


def ec2_tag(resource, **kwargs):
    """Tag a resource with specified tags.

    Example::
        tag(instance, Name='example.host')
    """
    connection = ec2_connect()
    connection.create_tags([resource.id], kwargs)
    mico.output.debug("tag instance %s:" % (
        resource.id,
        ",".join(map(lambda x:"%s=%s" % x, [x for x in kwargs.iteritems()]))
    ))

def ec2_tag_volumes(instance):
    """Tag volumes in the instance following a basic notation Name as
    hostname of the instance host and Device to the properly device in
    the system.
    """

    connection = ec2_connect()

    _obj = instance.get_attribute("blockDeviceMapping")
    if u"blockDeviceMapping" in _obj:
        _obj = _obj[u"blockDeviceMapping"]
        for device, obj in _obj.items():
            if obj.volume_id is not None:
                _d = { "Device": device }
                if "Name" in instance.tags:
                    _d["Name"] = instance.tags["Name"]
                connection.create_tags([obj.volume_id], _d)


def ec2_ensure(ami, name=None, address=None, wait_until_running=True,
               tags={}, force=False, region=None,
               termination_protection=True, volumes={}, **kwargs):
    """Create a new EC2 instance according with parameters passed as
    arguments.

    :type ami: string
    :param ami: An string which contains the AMI identifier for the
        instance.

    :type name: string
    :param name: a descriptive name for the host, this field will be used as
        Name tag for the host. If not present host will be no tagged for
        Name. Also you can override this tag using tag parameter.

    :type image_id: string
    :param image_id: The ID of the image to run.

    :type min_count: int
    :param min_count: The minimum number of instances to launch.

    :type max_count: int
    :param max_count: The maximum number of instances to launch.

    :type key_name: string
    :param key_name: The name of the key pair with which to
        launch instances.

    :type security_groups: list of strings
    :param security_groups: The names of the security groups with which to
        associate instances

    :type user_data: string
    :param user_data: The user data passed to the launched instances

    :type instance_type: string
    :param instance_type: The type of instance to run:

        * t1.micro
        * m1.small
        * m1.medium
        * m1.large
        * m1.xlarge
        * c1.medium
        * c1.xlarge
        * m2.xlarge
        * m2.2xlarge
        * m2.4xlarge
        * cc1.4xlarge
        * cg1.4xlarge
        * cc2.8xlarge

    :type placement: string
    :param placement: The availability zone in which to launch
        the instances.

    :type address: string
    :param address: the public IP address to associate with the instance.

    :type kernel_id: string
    :param kernel_id: The ID of the kernel with which to launch the
        instances.

    :type ramdisk_id: string
    :param ramdisk_id: The ID of the RAM disk with which to launch the
        instances.

    :type monitoring_enabled: bool

    :type region: string
    :param region: the region name where instance will live.

    :type wait_until_running: bool
    :param wait_until_running: when setting to True (the default), thread
        will be blocked until the instance status will be 'running', if
        false, function returns without check the instance status.

    :type tags: dict
    :param tags: a dictionary which contains tags for this instance.

    :type termination_protection: bool
    :param termination_protection: set the termination protection of the
        instance, by default all nodes are stated with termination
        protection set to true.

    :type force: bool
    :param force: if set to True force the creation tough the instance
        already exists (i.e. some other instance has the same tags.)

    :type volumes: dict
    :param volumes: a dictionary in the form {device: ebs_volume}, where
        device is a string which identify the aws device for the volume (i.e
        /dev/sdf), and ebs_volume is a volume object created by ebs_ensure.
    """

    if not force:
        _obj = ec2_exists({"Name": name})
        if _obj:
            status = _obj.update()
            if status != "terminated":
                mico.output.info("use existent instance: %s" % _obj.id)
                if getattr(_obj,"ip_address", None) and _obj.ip_address:
                    env.hosts.append(_obj.ip_address)
                    env.host_string = _obj.ip_address
                return _obj

    kwargs["disable_api_termination"] = termination_protection

    connection = ec2_connect()
    reservation = connection.run_instances(ami, **kwargs)
    instance = reservation.instances[0]

    status = instance.update()

    if name is not None:
        connection.create_tags([instance.id], { "Name": name })

    if tags:
        connection.create_tags([instance.id], tags)

    if not wait_until_running:
        return instance

    while status == 'pending':
        mico.output.debug("waiting 10 secs for instance initialiation...")
        time.sleep(10)
        status = instance.update()
    time.sleep(2) # yes... amazon weird behaviour :/

    for device, volume in volumes.items():
        connection.attach_volume(volume.id, instance.id, device)
        ec2_tag_volumes(instance)
        mico.output.info("attach volume %s as device %s at instance %s" % (
            volume.id,
            device,
            instance.id
        ))

    if not volumes:
        # tag only root device
        ec2_tag_volumes(instance)

    if address:
        mico.output.info("associated address %s at instance %s" % (
            address,
            instance.id
        ))
        connection.associate_address(instance.id, address)

    if getattr(instance,"ip_address", None) and instance.ip_address:
        mico.output.info("created instance: %s [%s]" % (instance.id, instance.ip_address))
        if 'mico' in env.roledefs:
            env.roledefs['mico'].append(instance.ip_address)
        else:
            env.roledefs['mico'] = [ instance.ip_address ]
    else:
        mico.output.info("created instance: %s [<unassigned address>]" % (instance.id,))

    time.sleep(2) # yes... another amazon weird behaviour :/

    return instance



def ec2_exists(tags={}):
    """Returns if tagged instance already exists, if exists return the object,
    otherwise returns None.
    """
    connection = ec2_connect()
    ret = []

    for reservation in connection.get_all_instances(None, dict(map(lambda (x,y):("tag:%s" % x, y), tags.items()))):
        for instance in reservation.instances:
            if instance.update() != "terminated":
                ret.append(instance)

    if len(ret) == 1:
        return ret[0]
    else:
        return ret

def ec2_list(*args):
    """List instances filtering with tag name, provided in arguments. Glob
    expressions are allowed in filters as multiple filters too, for
    example::

        ec2_list('host-*', '*database*')
    """
    conn = ec2_connect()
    chain = itertools.chain.from_iterable
    args = args or ('*',)

    for instance in chain([res.instances for res in conn.get_all_instances()]):
        if args:
            if "Name" in instance.tags:
                for arg in args:
                    if fnmatch(instance.tags["Name"], arg):
                        instance.name = instance.tags["Name"]
                        instance.secgroups = ",".join(map(
                            lambda x:x.name,
                            instance.groups
                        ))
                        yield instance.__dict__
        else:
            instance.name = instance.tags.get("Name", "None")
            instance.secgroups = ",".join(map(
                lambda x:x.name,
                instance.groups
            ))
            yield instance.__dict__


ec2_launch = ec2_create = ec2_run = ec2_ensure

from mico.lib.aws.ec2.sg  import *
from mico.lib.aws.ec2.cw  import *
from mico.lib.aws.ec2.eip import *
from mico.lib.aws.ec2.ebs import *
from mico.lib.aws.ec2.elb import *
from mico.lib.aws.ec2.autoscale  import *


from mico import run
from mico.environ import environ

@environ('ec2_ami')
def ec2_get_ami():
    return run("curl http://169.254.169.254/latest/meta-data/%s" % "ami-id")

@environ('ec2_hostname')
def ec2_get_hostname():
    return run("curl http://169.254.169.254/latest/meta-data/%s" % "hostname")

@environ('ec2_instance_action')
def ec2_get_instance_action():
    return run("curl http://169.254.169.254/latest/meta-data/%s" % "instance_action")

@environ('ec2_instance_type')
def ec2_get_instance_type():
    return run("curl http://169.254.169.254/latest/meta-data/%s" % "instance_type")

@environ('ec2_aki')
def ec2_get_aki():
    return run("curl http://169.254.169.254/latest/meta-data/%s" % "kernel-id")

@environ('ec2_local_hostname')
def ec2_get_local_hostname():
    return run("curl http://169.254.169.254/latest/meta-data/%s" % "local-hostname")

@environ('ec2_public_hostname')
def ec2_get_public_hostname():
    return run("curl http://169.254.169.254/latest/meta-data/%s" % "public-hostname")

@environ('ec2_local_ipv4')
def ec2_get_local_ipv4():
    return run("curl http://169.254.169.254/latest/meta-data/%s" % "local-ipv4")

@environ('ec2_public_ipv4')
def ec2_get_public_ipv4():
    return run("curl http://169.254.169.254/latest/meta-data/%s" % "public-ipv4")

@environ('ec2_mac')
def ec2_get_mac():
    return run("curl http://169.254.169.254/latest/meta-data/%s" % "mac")


