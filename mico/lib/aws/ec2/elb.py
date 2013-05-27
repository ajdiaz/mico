#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""The ELB submodule provide a way to manage Elastic Load Balancer resources
from AWS.
"""

from os import environ as os_environ

from boto.exception import BotoServerError
from boto.ec2 import get_region
from boto.ec2.elb import ELBConnection
from boto.ec2.elb import HealthCheck

import boto.ec2.elb

import mico.output
from mico.lib.aws.ec2 import EC2TemplateError
from mico.lib.aws.ec2 import ec2_connect


def elb_connect(region=None, *args, **kwargs):
    """Helper to connect to Amazon Web Services EC2, using identify provided
    by environment, as also optional region in arguments.
    """
    if not os_environ.get("AWS_ACCESS_KEY_ID", None):
        raise EC2TemplateError("Environment variable AWS_ACCESS_KEY_ID is not set.")
    if not os_environ.get("AWS_SECRET_ACCESS_KEY", None):
        raise EC2TemplateError("Environment variable AWS_SECRET_ACCESS_KEY is not set.")

    if not region:
        region = env.get("ec2_region")

    for reg in boto.ec2.elb.regions():
        if reg.name == region:
            region = reg

#    region = get_region(region,
#            aws_access_key_id = os_environ.get("AWS_ACCESS_KEY_ID"),
#            aws_secret_access_key = os_environ.get("AWS_ACCESS_SECRET_KEY")
#    )
#
    connection = ELBConnection(
            os_environ.get("AWS_ACCESS_KEY_ID"),
            os_environ.get("AWS_SECRET_ACCESS_KEY"),
            region = region,
            *args,
            **kwargs
    )
    return connection


def elb_check(target, interval=20, healthy_threshold=3,
        unhealthy_threshold=5):
    """Create a new ELB check.

    :type interval: int
    :param interval: Specifies how many seconds there are between
        health checks.

    :type target: str
    :param target: Determines what to check on an instance. See the
        Amazon HealthCheck_ documentation for possible Target values.

    .. _HealthCheck: http://docs.amazonwebservices.com/ElasticLoadBalancing/latest/APIReference/API_HealthCheck.html
    """
    return HealthCheck(
            target   = target,
            interval = interval,
            healthy_threshold = healthy_threshold,
            unhealthy_threshold = unhealthy_threshold
    )


def elb_listener(bind_port, remote_port, protocol, cert=None):
    """Create a new listener for ELB, with the specific configuration passed
    as argument.
    """

    if cert is not None:
        if isinstance(cert, str):
            return (bind_port, remote_port, protocol, cert)
        else:
            return (bind_port, remote_port, protocol, cert.arn)
    else:
        return (bind_port, remote_port, protocol)


def elb_ensure(name, listeners, check, zones=None, *args, **kwargs):
    """Create a new ELB

    :type name: string
    :param name: the name of the elb, if exists, the same object will be
        returned, unless force parameter if set to True

    :type listeners: a list of listener object
    :param listeners: the listeners of the ELB

    :type zones: list of strings
    :param zones: the availability zones where ELB must be span.

    :type check: a elb_check
    :param check: the health check to be used.
    """

    _obj = elb_exists(name)
    if _obj:
        mico.output.info("using existent ELB: %s" % name)
        return _obj

    connection = elb_connect()

    if zones is None:
        ec2_conn = ec2_connect()
        zones = ec2_conn.get_all_zones()

    elb = connection.create_load_balancer(
            name = name,
            zones = zones,
            listeners = listeners,
            *args,
            **kwargs
    )

    elb.configure_health_check(check)
    elb = elb_exists(name)
    mico.output.info("created new ELB: %s" % name)
    return elb


def elb_exists(name):
    """Returns the ELB which match with specified name.
    """

    connection = elb_connect()
    try:
        return connection.get_all_load_balancers([name])[0]
    except BotoServerError:
        return []

