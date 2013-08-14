#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""The sg library provides methods to work with AWS EC2 security
groups.
"""

import socket

from boto.exception import EC2ResponseError
from boto.ec2.elb.securitygroup import SecurityGroup
from boto.ec2.securitygroup import SecurityGroup as SG_Instance

import mico.output
from mico.util.dicts import AttrDict
from mico.lib.aws.ec2 import ec2_connect, ec2_list
from mico.lib.aws.ec2 import EC2LibraryError

def sg_rule(protocol="tcp", source="0.0.0.0/32", port=None, from_port=None, to_port=None):
    """Return a representation of a specific security rule.
    """

    cidr_ip = None
    src_group_name = None
    ret = { "ip_protocol": protocol }

    if port is not None:
        if isinstance(port, int):
            ret["from_port"] = port
            ret["to_port"]   = port
        elif isinstance(port, str):
            if "-" in port:
                port_ini, port_end = port.split("-")
                ret["from_port"] = int(port_ini)
                ret["to_port"]   = int(port_end)
            else:
                ret["from_port"] = int(port)
                ret["to_port"]   = int(port)
    else:
        if protocol != "icmp":
            ret["from_port"] = from_port or 0
            ret["to_port"]   = to_port or 65535

    def _add_source(src, d):
        r = {}
        r.update(d)
        if isinstance(src, SecurityGroup) or \
           isinstance(src, SG_Instance):

            if getattr(src, "owner_alias", None):
                # XXX: Monkey Patch!!
                src.owner_id = src.owner_alias
            r["src_group"] = src

        elif isinstance(src, str) or isinstance(src, unicode):
            if "/" in src and "." in src:
                # TODO: better ip check is desired here.
                r["cidr_ip"] = src
            else:
                r["src_group"] = sg_exists(src)
                if r["src_group"] is None:
                    raise KeyError("security group %s does not exists" % src)
        else:
            raise ValueError("Unknow type for sg source")
        return r


    if isinstance(source, list):
        return [ _add_source(x, ret) for x in source ]
    else:
        return [ _add_source(source, ret)]

def sg_ensure(name, description, vpc_id=None, rules=[], force=False):
    """Create a new EC2 security group according with parameters passed
    as arguments.

    :type name: string
    :param name: The name of the new security group

    :type description: string
    :param description: The description of the new security group

    :type vpc_id: string
    :param vpc_id: The ID of the VPC to create the security group in,
         if any.

    :type rules: list
    :param rules: a list of objects rules.
    """
    connection = ec2_connect()

    _obj = sg_exists(name)
    if _obj:
        mico.output.info("use existent security group: %s" % name)
        if not force:
            return _obj
    elif not _obj:
        _obj = connection.create_security_group(name, description, vpc_id)
        mico.output.info("create security group: %s" % name)

    for rule in rules:
        for r in rule:
            try:
                _obj.authorize(**r)
                mico.output.info("add rule to security group %s: %s" % (
                    _obj.name,
                    ",".join(map(lambda x:"%s=%s" % x, r.items()))
                ))
            except EC2ResponseError as e:
                if e.error_code == "InvalidPermission.Duplicate":
                    mico.output.debug("skip add already exists rule to security group %s: %s" % (
                        _obj.name,
                        ", ".join(map(lambda x:"%s=%s" % x, r.items()))
                    ))
            except Exception as e:
                raise e

    return _obj

def sg_exists(name):
    """Return the security group with name passed as argument for specified
    region or None if it does not exists.
    """
    connection = ec2_connect()

    _sg = connection.get_all_security_groups()
    _sg = [g for g in _sg if g.name == name]

    if len(_sg) > 0:
        return _sg[0]
    else:
        return None

def _sg_revoke_all_rules(name, target):
    for rule in name.rules:
        dr = rule.__dict__
        if target.id in [g.group_id for g in dr["grants"]]:
            name.revoke(
                ip_protocol = dr["ip_protocol"],
                from_port = dr["from_port"],
                to_port = dr["to_port"],
                src_group = target
            )

def sg_delete(name, force=False):
    """Deletes a security group.
    If you attempt to delete a security group that contains instances, or is referenced
    by another security group, the operation fails. Use the "force" flag to delete a security
    group that is referenced by another security group.

    :type name: string
    :param name: The name of the security group

    :type force: boolean
    :param force: Delete a security group even when it is referenced by another security group
    by deleting the referencing rules.
    """
    connection = ec2_connect()

    target = sg_exists(name)
    if target:
        if force:
            instances = [x for x in ec2_list('sec:%s' % (target.name, ))]
            if instances:
                raise EC2LibraryError('%s is in use by %s.' % (target.name, ",".join(map(lambda x:x.name, instances)),))
            _sg = connection.get_all_security_groups()
            for sg in filter(lambda x: x.name != target.name, _sg):
                mico.output.debug("Forcing ")
                _sg_revoke_all_rules(sg, target)
        connection.delete_security_group(target.name)
        # boto.ec2.connection.delete_security_group() raises boto.exception.EC2ResponseError
        # if the target security group is referenced by another security group
        return target
    else:
        raise EC2LibraryError('%s does not exist.' % (name, ))
