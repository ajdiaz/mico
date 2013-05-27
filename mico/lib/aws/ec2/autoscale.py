#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""The EC2 autoscale template provides methods to work with AWS autoscale
techniques.
"""

import time
from os import environ as os_environ
from fnmatch import fnmatch

import boto.ec2.autoscale
from boto.ec2.securitygroup import SecurityGroup
from boto.ec2.autoscale import AutoScaleConnection
from boto.ec2.autoscale import LaunchConfiguration
from boto.ec2.autoscale import AutoScalingGroup
from boto.ec2.autoscale import ScalingPolicy
from boto.ec2.autoscale import Tag

import mico.output
from mico.lib.aws.ec2 import EC2TemplateError
from mico.lib.aws.ec2 import ec2_connect, get_region
from mico.lib.aws.ec2 import ec2_tag_volumes
from mico.lib.aws.ec2.cw import cw_connect, _cw_define
from mico.lib.aws.ec2 import ec2_connect


@sync
def _as_get_timestamp():
    # TODO: In the future this function will be in utils package.
    if not getattr(_as_get_timestamp, "_timestamp", None):
        _as_get_timestamp._timestamp = time.strftime("%Y%m%d%H%S",time.localtime())
    return _as_get_timestamp._timestamp

def as_connect(region=None, *args, **kwargs):
    """Helper to connect to Amazon Web Services EC2, using identify provided
    by environment, as also optional region in arguments.
    """
    if not os_environ.get("AWS_ACCESS_KEY_ID", None):
        raise EC2TemplateError("Environment variable AWS_ACCESS_KEY_ID is not set.")
    if not os_environ.get("AWS_SECRET_ACCESS_KEY", None):
        raise EC2TemplateError("Environment variable AWS_SECRET_ACCESS_KEY is not set.")

    if not region:
        region = env.get("ec2_region")

    for reg in boto.ec2.autoscale.regions():
        if reg.name == region:
            region = reg

    connection = AutoScaleConnection(
            os_environ.get("AWS_ACCESS_KEY_ID"),
            os_environ.get("AWS_SECRET_ACCESS_KEY"),
            region = region,
            *args,
            **kwargs
    )

    return connection

def as_config_exists(name):
    """Return the instance template with specific name."""
    connection = as_connect()
    return connection.get_all_launch_configurations(names=[name])

def as_config(name, ami, force=False, *args, **kwargs):
    """Create a template instance to be used in autoscale group. In general
    this template will be defined as another standalone instance, according
    to paramenters for :func:`ec2_instance` function.

    :type ami: string
    :param ami: An string which contains the AMI identifier for the
        instance.

    :type name: string
    :param name: a descriptive name for the host, this field will be used as
        Name tag for the host. If not present host will be no tagged for
        Name. Also you can override this tag using tag parameter.

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
    """

    _obj = as_config_exists(name)
    if _obj:
        if not force:
            mico.output.info("use existent config %s" % name)
            return _obj[0]
    if force:
        name = "%s-%s" % (name, _as_get_timestamp())

    _sgs = None
    if "security_groups" in kwargs:
        if not isinstance(kwargs["security_groups"], list):
            _sgs = [ kwargs["security_groups"] ]
        else:
            _sgs = kwargs["security_groups"]

        _sgs = map(
                lambda x:x.name if isinstance(x, SecurityGroup) else x,
                _sgs
        )

    kwargs["security_groups"] = _sgs

    connection = as_connect()

    config = LaunchConfiguration(
            name=name,
            image_id=ami,
            instance_monitoring=True,
            *args,
            **kwargs)

    connection.create_launch_configuration(config)

    mico.output.info("create new config %s" % name)
    return config

def as_policy(name, adjustment_type='ChangeInCapacity',
        scaling_adjustment=2, cooldown=60, *args, **kwargs):
    """
    Scaling Policy

    :type name: str
    :param name: Name of scaling policy.

    :type adjustment_type: str
    :param adjustment_type: Specifies the type of adjustment. Valid values are `ChangeInCapacity`, `ExactCapacity` and `PercentChangeInCapacity`.

    :type scaling_adjustment: int
    :param scaling_adjustment: Value of adjustment (type specified in `adjustment_type`).

    :type cooldown: int
    :param cooldown: Time (in seconds) before Alarm related Scaling Activities can start after the previous Scaling Activity ends.
    """

    name = "%s-%s" % (name, _as_get_timestamp())
    _x = {
            "name": name,
            "adjustment_type": adjustment_type,
            "scaling_adjustment": scaling_adjustment,
            "cooldown": cooldown
    }
    _x.update(kwargs)
    return _x

def as_exists(name):
    """Return a list of autoscale groups which match with specific name."""
    connection = as_connect()
    return connection.get_all_groups(names = [name])

def as_ensure(
        name,
        zones,
        instance,
        balancers = [],
        events = [],
        min_size = 2,
        max_size = 20,
        desired_size = None,
        force = False
):
    """Create a new autoscale group.

    :type name: str
    :param name: the name of the autoscale group to be created

    :type zones: list of str
    :param zones: a list of the availability zones where autoscale group
        will be working on.

    :type instance: instance_template object
    :param instance: an instance template, created by as_instance.

    :type balancers: list of balancers
    :param balancers: a list of balancers where new instances will be
        autoattached.

    :type events: list of events
    :param events: a list of events created with as_event, which define in
        what conditions the autoscale group will be grow up.
    """

    connection = as_connect()

    if force:
        ag_name = "%s-%s" % (name, _as_get_timestamp())
    else:
        ag_name = name

    _obj = as_exists(ag_name)
    if _obj:
        if not force:
            ag = _obj[0]
            mico.output.info("use existent autoscaling group: %s" % ag_name)
            return ag

    _l = []
    for elb in balancers:
        if isinstance(elb, str):
            _l.append(elb)
        else:
            _l.append(elb.name)

    ag = AutoScalingGroup(
            name = ag_name,
            availability_zones = zones,
            launch_config = instance,
            load_balancers = _l,
            min_size = min_size,
            max_size = max_size,
            desired_capacity = desired_size
    )
    connection.create_auto_scaling_group(ag)
    mico.output.info("created new autoscaling group: %s" % ag_name)

    as_tag = Tag(key='Name', value = "%s" % name, propagate_at_launch=True, resource_id=ag_name)

    # Add the tag to the autoscale group
    connection.create_or_update_tags([as_tag])

    cw_connection = cw_connect()
    for condition, actions in events:
        if not isinstance(actions, list):
            actions = [ actions ]

        condition.dimensions = {"AutoScalingGroupName": ag_name}

        # XXX: boto does not handle very well the alarm_actions list when the
        # same connection is used for two different cloudwatch alarms, so the
        # actions appears to be duplicated in both alarms. We need to force the
        # internal list to be empty.
        condition.alarm_actions = []

        for action in actions:
            policy = ScalingPolicy(action["name"], as_name=ag_name, **action)
            mico.output.info("create policy %s" % policy.name)
            connection.create_scaling_policy(policy)

            action = connection.get_all_policies(as_group=ag_name,policy_names=[action["name"]])[0]
            condition.name = "%s-%s" % (condition.name, _as_get_timestamp())
            condition.add_alarm_action(action.policy_arn)
            mico.output.debug("add new alarm for condition %s: %s" % (condition.name, action.name))

        cw_connection.create_alarm(condition)
        mico.output.info("create alarm %s" % condition.name)
    return ag

def as_alarm(name, alarm_actions=[], *args, **kwargs):
    """Ensures that an specific alarm for autoscale group
    exists in cloudwatch.

    :type name: str
    :param name: Name of alarm.

    :type metric: str
    :param metric: Name of alarm's associated metric.

    :type namespace: str
    :param namespace: The namespace for the alarm's metric.

    :type statistic: str
    :param statistic: The statistic to apply to the alarm's associated
                      metric.
                      Valid values: SampleCount|Average|Sum|Minimum|Maximum

    :type comparison: str
    :param comparison: Comparison used to compare statistic with threshold.
                           Valid values: >= | > | < | <=

    :type threshold: float
    :param threshold: The value against which the specified statistic
                      is compared.

    :type period: int
    :param period: The period in seconds over which teh specified
                   statistic is applied.

    :type evaluation_periods: int
    :param evaluation_period: The number of periods over which data is
                              compared to the specified threshold.

    :type unit: str
    :param unit: Allowed Values are:
                 Seconds|Microseconds|Milliseconds,
                 Bytes|Kilobytes|Megabytes|Gigabytes|Terabytes,
                 Bits|Kilobits|Megabits|Gigabits|Terabits,
                 Percent|Count|
                 Bytes/Second|Kilobytes/Second|Megabytes/Second|
                 Gigabytes/Second|Terabytes/Second,
                 Bits/Second|Kilobits/Second|Megabits/Second,
                 Gigabits/Second|Terabits/Second|Count/Second|None
    """
    return _cw_define(name, alarm_actions, *args, **kwargs)

def as_event(condition, action):
    """Create a new definition of an event which produces an action.

    :type condition: a cw metric
    :param condition: a cw metric created with cw_ensure

    :type action: an autoscale policy
    :param action: an autoscale policy created with as_policy
    """

    return (condition, action)

def as_delete(name, foce=False):
    """Remove a autoscale group.

    :type name: str
    :param name: the name of the autoscale group to be removed.

    :type force: bool
    :param force: if set to True (default False) remove autoscaling group
        even tough there will running instances.
    """
    conn = as_connect()
    return conn.delete_auto_scaling_group(name, force)


def as_delete_policy(name, autoscale_group=None):
    """Remove a policy

    :type name: str
    :param name: the name or ARN of the policy to be removed.

    :type autoscale_group: str
    :param autoscale_group: the name of the autoscale group.
    """
    conn = as_connect()
    return conn.delete_policy(name, autoscale)

def as_delete_config(name):
    """Remove a config template

    :type name: str
    :param name: the name of the config template
    """
    conn = as_connect()
    return conn.delete_launch_configuration(name)

def as_activity(name, max_records=None):
    """Get the scaling activity for an autoscale group

    :type name: str
    :param name: the name of the autoscale group

    :type max_records: int or None
    :param max_records: the maximum number of record to get, or None (by
        default) to get all of them.
    """
    conn = as_connect()
    return conn.get_all_activities(name, max_records)

def as_list(*args):
    """List autoscaling groups filtering by autoscale name, provided as
    argument. Glob expressiosn are allowed in filters as multiple filtes
    too, for example::

        as_list('apaches-*')
    """
    conn = as_connect()
    ec2  = ec2_connect()
    args = args or ('*',)

    for group in conn.get_all_groups():
        for arg in args:
            if fnmatch(group.name, arg):
                _i = [i.instance_id for i in group.instances]
                if len(_i) > 0:
                    instances = [
                            i for r in ec2.get_all_instances(_i)
                            for i in r.instances
                    ]
                    for instance in instances:
                        instance.name = instance.tags.get("Name", None)
                        instance.secgroups = ",".join(map(
                            lambda x:x.name,
                            instance.groups
                        ))
                        instance.autoscaling_group = group.name
                        yield instance.__dict__

