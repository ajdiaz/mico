#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""The sg template provides methods to work with AWS EC2 security
groups.
"""

import socket

from boto.exception import EC2ResponseError
from boto.ec2.elb.securitygroup import SecurityGroup
from boto.ec2.securitygroup import SecurityGroup as SG_Instance

import mico.output
from mico.util.dicts import AttrDict
from mico.lib.aws.ec2 import ec2_connect

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
        if isinstance(src, SecurityGroup) or \
           isinstance(src, SG_Instance):

            if getattr(src, "owner_alias", None):
                # XXX: Monkey Patch!!
                src.owner_id = src.owner_alias
            d["src_group"] = src

        elif isinstance(src, str) or isinstance(src, unicode):
            if "/" in src and "." in src:
                # TODO: better ip check is desired here.
                d["cidr_ip"] = src
            else:
                d["src_group"] = sg_exists(src)
                if d["src_group"] is None:
                    raise KeyError("security group %s does not exists" % src)
        else:
            raise ValueError("Unknow type for sg source")
        return d


    if isinstance(source, list):
        for s in source:
            yield _add_source(s, ret)
    else:
        yield _add_source(source, ret)


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
    """Return the ecurity group with name passed as argument for specified
    region or None if it does not exists.
    """
    connection = ec2_connect()

    _sg = connection.get_all_security_groups()
    _sg = [g for g in _sg if g.name == name]

    if len(_sg) > 0:
        return _sg[0]
    else:
        return None


