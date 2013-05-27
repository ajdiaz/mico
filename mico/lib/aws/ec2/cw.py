#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""The cloudwatch module allows to access to AWS Cloud Watch API"""

from os import environ as os_environ

from boto.ec2.cloudwatch import CloudWatchConnection
from boto.ec2.cloudwatch import MetricAlarm

import mico.output
from mico.lib.aws.ec2 import EC2TemplateError

import boto.ec2.cloudwatch

def cw_connect(region=None, *args, **kwargs):
    """Helper to connect to Amazon Web Services EC2, using identify provided
    by environment, as also optional region in arguments.
    """
    if not os_environ.get("AWS_ACCESS_KEY_ID", None):
        raise EC2TemplateError("Environment variable AWS_ACCESS_KEY_ID is not set.")
    if not os_environ.get("AWS_SECRET_ACCESS_KEY", None):
        raise EC2TemplateError("Environment variable AWS_SECRET_ACCESS_KEY is not set.")

    if not region:
        region = env.get("ec2_region")

    for reg in boto.ec2.cloudwatch.regions():
        if reg.name == region:
            region = reg

    connection = CloudWatchConnection(
            os_environ.get("AWS_ACCESS_KEY_ID"),
            os_environ.get("AWS_SECRET_ACCESS_KEY"),
            region = region
    )

    return connection


def cw_exists(name):
    """Return the metric which match with specific name"""
    connection = cw_connect()
    return connection.list_metrics(metric_name=name)


def _cw_define(name, alarm_actions=[], *args, **kwargs):
    _obj = cw_exists(name)
    if _obj:
        mico.output.info("use existent cloudwatch metric: %s" % name)
        return _obj

    if "namespace" not in kwargs:
        kwargs["namespace"] = "AWS/EC2"


    _x = MetricAlarm(name = name, alarm_actions = alarm_actions, *args, **kwargs)

    # XXX: boto does not handle very well the alarm_actions list when the
    # same connection is used for two different cloudwatch alarms, so the
    # actions appears to be duplicated in both alarms. We need to force the
    # internal list to be empty.
    _x.alarm_actions = []

    for action in alarm_actions:
        mico.output.debug("add new alarm for metric %s: %s" % (name, action.name))
        _x.add_alarm_action(action.policy_arn)

    return _x

def cw_ensure(name, alarm_actions=[], *args, **kwargs):
    """
    Ensures that an specific alarm exists in cloudwatch.

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
    alarm = _cw_define(name, alarm_actions, *args, **kwargs)
    cw_connection = cw_connect()
    cw_connection.create_alarm(alarm)
    mico.output.info("create alarm %s" % name)
    return alarm

