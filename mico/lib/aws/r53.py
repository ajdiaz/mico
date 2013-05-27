#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""The route53 module offers functions to handle AWS Route53 DNS records."""

from os import environ as os_environ
from fnmatch import fnmatch
from boto.route53.connection import Route53Connection

class Route53TemplateError(Exception):
    """Models a Route53 template error."""

def r53_connect(region=None, *args, **kwargs):
    """Helper to connect to Amazon Web Services Route53, using identify provided
    by environment, as also optional region in arguments.

    .. note:: The region parameter is allowed, but do nothing, still here
        for future API compatibility and orthogonality between templates.
    """

    if not os_environ.get("AWS_ACCESS_KEY_ID", None):
        raise Route53TemplateError("Environment variable AWS_ACCESS_KEY_ID is not set.")
    if not os_environ.get("AWS_SECRET_ACCESS_KEY", None):
        raise Route53TemplateError("Environment variable AWS_SECRET_ACCESS_KEY is not set.")

    connection = Route53Connection(
            os_environ.get("AWS_ACCESS_KEY_ID"),
            os_environ.get("AWS_SECRET_ACCESS_KEY"),
            *args, **kwargs
    )

    return connection

def r53_zone_ensure(zone, caller_reference=None, comment='', force=False):
    """Create a hosted zone, returning the nameservers"""

    connection = connect()

    _obj = r53_zone_exists(zone)
    if _obj:
        return _obj[0]['Id'].split("/")[-1]
    else:
        response = connection.create_hosted_zone(zone, caller_reference, comment)
        return response['CreateHostedZoneResponse']['HostedZone']['Id'].split("/")[-1]

def r53_zone_remove(domainname):
    """Delete a hosted zone by ID"""

    connection = connect()

    response = connection.get_all_hosted_zones()

    response = filter(lambda x:x["Name"] == domainname,
           response['ListHostedZonesResponse']['HostedZones'])

    ret = []
    for x in response:
        ret.append(connection.delete_hosted_zone(x['Id'].split('/')[-1]))
    return ret

def r53_zone_exists(filter_expr='*'):
    """List all hosted zones"""

    connection = connect()
    response = connection.get_all_hosted_zones()
    return filter(lambda x:fnmatch(x["Name"], filter_expr),
                  response['ListHostedZonesResponse']['HostedZones'])

def r53_zone_get(hosted_zone_id, type=None, name=None, maxitems=None):
    """Get all the records for a single zone"""

    conn = connect()
    response = conn.get_all_rrsets(hosted_zone_id, type, name, maxitems=maxitems)
    # If a maximum number of items was set, we limit to that number
    # by turning the response into an actual list (copying it)
    # instead of allowing it to page

    conn = connect()
    if maxitems:
        response = response[:]
    return response

def _add_del(conn, hosted_zone_id, change, name, type, identifier, weight,
            values, ttl, comment):
    from boto.route53.record import ResourceRecordSets
    changes = ResourceRecordSets(conn, hosted_zone_id, comment)
    change = changes.add_change(change, name, type, ttl,
                                identifier=identifier, weight=weight)
    for value in values:
        change.add_value(value)
    return changes.commit()

def _add_del_alias(conn, hosted_zone_id, change, name, type, identifier, weight, alias_hosted_zone_id, alias_dns_name, comment):
    from boto.route53.record import ResourceRecordSets
    changes = ResourceRecordSets(conn, hosted_zone_id, comment)
    change = changes.add_change(change, name, type,
                                identifier=identifier, weight=weight)
    change.set_alias(alias_hosted_zone_id, alias_dns_name)
    return changes.commit()

def r53_record_exists(hosted_zone_id, name):
    """Return the record requested if exists or None if none found."""
    return filter(lambda x:x.name == name, r53_zone_get(hosted_zone_id, name=name))


def r53_record_ensure(zone, name, type, values, ttl=600,
               identifier=None, weight=None, comment="", force=False):
    """Add a new record to a zone.  identifier and weight are optional."""

    conn = connect()

    if name[-1] != ".":
        response = conn.get_all_hosted_zones()
        domain = filter(lambda x:x["Id"].split("/")[-1] == zone,
                  response['ListHostedZonesResponse']['HostedZones'])
        if (len(domain) > 0):
            domain = domain[0]["Name"]
            name = "%s.%s" % (name, domain)

    if not force:
        _obj = r53_record_exists(zone, name)
        if _obj:
            return _obj

    return _add_del(conn, zone, "CREATE", name, type, identifier,
                    weight, values, ttl, comment)

def r53_record_remove(hosted_zone_id, name, type, values, ttl=600,
               identifier=None, weight=None, comment=""):
    """Delete a record from a zone: name, type, ttl, identifier, and weight must match."""

    conn = connect()
    return _add_del(conn, hosted_zone_id, "DELETE", name, type, identifier,
             weight, values, ttl, comment)

def r53_alias_ensure(hosted_zone_id, name, type, alias_hosted_zone_id,
              alias_dns_name, identifier=None, weight=None, comment=""):
    """Add a new alias to a zone.  identifier and weight are optional."""

    conn = connect()
    return _add_del_alias(conn, hosted_zone_id, "CREATE", name, type, identifier,
                   weight, alias_hosted_zone_id, alias_dns_name, comment)

def r53_alias_remove(hosted_zone_id, name, type, alias_hosted_zone_id,
              alias_dns_name, identifier=None, weight=None, comment=""):
    """Delete an alias from a zone: name, type, alias_hosted_zone_id, alias_dns_name, weight and identifier must match."""

    conn = connect()
    return _add_del_alias(conn, hosted_zone_id, "DELETE", name, type, identifier,
                   weight, alias_hosted_zone_id, alias_dns_name, comment)

def r53_record_change(hosted_zone_id, name, type, newvalues, ttl=600,
                   identifier=None, weight=None, comment=""):
    """Delete and then add a record to a zone.  identifier and weight are optional."""

    conn = connect()
    from boto.route53.record import ResourceRecordSets
    changes = ResourceRecordSets(conn, hosted_zone_id, comment)
    # Assume there are not more than 10 WRRs for a given (name, type)
    responses = conn.get_all_rrsets(hosted_zone_id, type, name, maxitems=10)
    for response in responses:
        if response.name != name or response.type != type:
            continue
        if response.identifier != identifier or response.weight != weight:
            continue
        change1 = changes.add_change("DELETE", name, type, response.ttl,
                                     identifier=response.identifier,
                                     weight=response.weight)
        for old_value in response.resource_records:
            change1.add_value(old_value)

    change2 = changes.add_change("CREATE", name, type, ttl,
            identifier=identifier, weight=weight)
    for new_value in newvalues.split(','):
        change2.add_value(new_value)
    return changes.commit()

def r53_alias_change(hosted_zone_id, name, type, new_alias_hosted_zone_id,
                     new_alias_dns_name, identifier=None, weight=None, comment=""):
    """Delete and then add an alias to a zone.  identifier and weight are optional."""

    conn = connect()
    from boto.route53.record import ResourceRecordSets
    changes = ResourceRecordSets(conn, hosted_zone_id, comment)
    # Assume there are not more than 10 WRRs for a given (name, type)
    responses = conn.get_all_rrsets(hosted_zone_id, type, name, maxitems=10)
    for response in responses:
        if response.name != name or response.type != type:
            continue
        if response.identifier != identifier or response.weight != weight:
            continue
        change1 = changes.add_change("DELETE", name, type, 
                                     identifier=response.identifier,
                                     weight=response.weight)
        change1.set_alias(response.alias_hosted_zone_id, response.alias_dns_name)
    change2 = changes.add_change("CREATE", name, type, identifier=identifier, weight=weight)
    change2.set_alias(new_alias_hosted_zone_id, new_alias_dns_name)
    return changes.commit()

