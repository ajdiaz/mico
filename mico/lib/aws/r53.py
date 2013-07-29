#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""The r53 library offers functions to handle AWS Route53 DNS records.
"""

from os import environ as os_environ
from fnmatch import fnmatch
from boto.route53.connection import Route53Connection

class R53LibraryError(Exception):
    """Models a R53 library error."""

def r53_connect(region=None, *args, **kwargs):
    """Helper to connect to Amazon Web Services Route53, using identify provided
    by environment, as also optional region in arguments.

    .. note:: The region parameter is allowed, but do nothing, still here
        for future API compatibility and orthogonality between libraries.
    """

    if not os_environ.get("AWS_ACCESS_KEY_ID", None):
        raise R53LibraryError("Environment variable AWS_ACCESS_KEY_ID is not set.")
    if not os_environ.get("AWS_SECRET_ACCESS_KEY", None):
        raise R53LibraryError("Environment variable AWS_SECRET_ACCESS_KEY is not set.")

    connection = Route53Connection(
            os_environ.get("AWS_ACCESS_KEY_ID"),
            os_environ.get("AWS_SECRET_ACCESS_KEY"),
            *args, **kwargs
    )

    return connection

def r53_zones(name=None):
    conn = r53_connect()

    if name is None:
        return conn.get_zones()
    else:
        return [ conn.get_zone(name) ]

def r53_records(zone, name=None):
    conn = r53_connect()

    if name is None:
        return zone.get_records()
    else:
        return [ zone.get_record(name) ]

def r53_list(*args):
    """Get all records in R53.
    """
    args = args or ('*',)

    for zone in r53_zones():
        for record in r53_records(zone):
            for arg in args:
                if fnmatch(record.name, arg):
                    record.zone = zone.name
                    record.zone_obj = zone
                    yield record

