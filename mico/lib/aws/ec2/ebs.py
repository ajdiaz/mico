#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""The EC2 volume template provides methods to work with AWS EC2 EBS volumes.
"""

from fnmatch import fnmatch

import mico.output

from mico.lib.aws.ec2 import ec2_connect
from mico.lib.aws.ec2 import ec2_tag_volumes
from mico.lib.aws.ec2 import EC2TemplateError


def ebs_ensure(size, zone=None, instance=None, device=None, tags={},
               force=False, **kwargs):
    """Create a new EBS volume

    :type size: int
    :param size: The size of the new volume, in GiB

    :type zone: string or :class:`boto.ec2.zone.Zone`
    :param zone: The availability zone in which the Volume will be created.

    :type snapshot: string or :class:`boto.ec2.snapshot.Snapshot`
    :param snapshot: The snapshot from which the new Volume will be
        created.

    :type volume_type: string
    :param volume_type: The type of the volume. (optional).  Valid
        values are: standard | io1.

    :type iops: int
    :param iops: The provisioned IOPs you want to associate with
        this volume. (optional)

    :type tags: dict
    :param tags: a dictionary of tags for this volume.

    :type force: bool
    :param force: if set to True force the creation of the volumen tough
        already exists other volume with the same tags.
    """

    if zone is None and instance is None:
        raise EC2TemplateError("volume require zone or instance to be created.")

    if zone is None:
        zone = instance.placement

    if not force and tags:
        _obj = ebs_exists(tags)
    elif not force:
        _tags = {}
        if instance is not None:
            if "Name" in instance.tags:
                _tags["Name"] = instance.tags["Name"]
        if device is not None:
            _tags["Device"] = device
        if _tags:
            _obj = ebs_exists(_tags)
        else:
            _obj = None
    else:
        _obj = None

    if _obj:
        mico.output.info("use existent volume: %s" % _obj[0].id)
        return _obj[0]

    connection = ec2_connect()

    _obj = connection.create_volume(size, zone, **kwargs)
    mico.output.info("create volume: %s (size=%s, zone=%s)" % (
        _obj.id,
        size,
        zone
    ))

    if tags:
        connection.create_tags([_obj.id],tags)

    if device and instance:
        connection.attach_volume(_obj.id, instance.id, device)
        ec2_tag_volumes(instance)
        mico.output.info("attach volume %s as device %s at instance %s" % (
            _obj.id,
            device,
            instance.id
        ))


def ebs_exists(tags={}):
    """Returns if tagged volume already exists, if exists return the object,
    otherwise returns None.
    """
    connection = ec2_connect()

    _x = connection.get_all_volumes(None,
            dict(map(lambda (x,y):("tag:%s" % x, y), tags.items())))
    return filter(lambda x:x.status == 'in-use', _x)


def ebs_list(*args):
    """List volumes filtering with tag name, provided in arguments. Glob
    expressions are allowed in filters as multiple filters too, for
    example::

        ebs_list('host-*', '*database*')
    """
    conn = ec2_connect()
    vol = conn.get_all_volumes()
    ins = dict(map(lambda x:(x.id,x), [i for r in conn.get_all_instances() for i in r.instances]))
    args = args or ('*',)

    for x in vol:
        x.name = x.tags.get("Name", None)
        for arg in args:
            if x.name and fnmatch(x.name, arg):
               x.device = x.attach_data.device
               x.instance_id = ("%s (%s)" % (ins[x.attach_data.instance_id].tags.get("Name",None), x.attach_data.instance_id)) \
                               if x.attach_data.id is not None else None
               yield x.__dict__


