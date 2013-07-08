#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""The network core submodule provide a useful way to manage network
interfaces in remote machine."""

import os
import mico

from fabric.api import hide
from fabric.api import settings


def network_interfaces():
    """Return a list of available network interfaces in the remote host."""
    with settings(hide('running', 'stdout')):
         res = mico.run("/sbin/ifconfig -s")
         return map(lambda line: line.split(' ')[0], res.splitlines()[1:])

def network_address(iface=""):
    """Return a list of IP addresses associated with an specific interface
    or, if not provided, the full list of the system."""
    with settings(hide('running', 'stdout')):
         res = mico.run("/sbin/ifconfig %s | grep 'inet addr'" % iface)
         return map(lambda x:x.split()[1].split(':')[1],
                    res.splitlines())

def network_netmask(iface=""):
    """Return a list of IP netmask associated with an specific interface
    or, if not provided, the full list of the system."""
    with settings(hide('running', 'stdout')):
         res = mico.run("/sbin/ifconfig %s | grep 'inet addr'" % iface)
         ret = []
         for _res in res.splitlines():
             field = _res.split()[2]
             if field.startswith("Mask"):
                 ret.append( field.split(':')[1] )
             else:
                 field = res.split()[3]
                 ret.append( field.split(':')[1] )
         return ret

def network_nameservers():
    """Return a list with the nameservers present in the remote system."""
    with settings(hide('running', 'stdout')):
        res = mico.run("grep ^nameserver /etc/resolv.conf")
        return map(lambda x:x.split()[1],res.splitlines())

