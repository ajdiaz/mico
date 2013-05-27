#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""The environ module provides a number of environ variables, which will be
used in your definitions and templates to ensure the correct way to do
actions. Usual environments are related with remote host, like installed
operating system, versions and so on.

Also, this module provides a decorator to create new environment
properties."""

import sys

import mico
from mico.util.dicts import AttrLazyDict

def environ(name):
    """Decorator to set new environment variables. Using this decoration you
    can create environment dynamic properties, for example, you can set new
    one environ called 'uptime' which contains the remote system uptime
    using the core template function 'uptime'::

        @environ('uptime')
        def _env_uptime():
            return mico.lib.core.uptime()

    Then you can use the new custom environ in the form::

        print env.custom.uptime

    Or in the old and good dictionary style::

        print env.custom["uptime"]

    """

    def _decorator(fn):
        setattr(sys.modules[__name__], name, fn)
        mico.env.custom[name] = fn
    return _decorator


@environ('kernel')
def _env_kernel():
    """Get the kernel version running in the remote host.
    """
    return mico.run("uname -s").lower()

from mico.lib.core import file_exists
from mico.lib.core import file_read

@environ('operating_system')
def _env_operation_system():
    """Get the Operating System of the remote host.
    """
    # TODO: Add other operating systems here...
    if env.custom.kernel == "linux":
        if file_exists("/etc/lsb-release"):
            return "ubuntu"
        if file_exists("/etc/debian_version"):
            return "debian"
        if file_exists("/etc/gentoo-release"):
            return "gentoo"
        if file_exists("/etc/fedora-release"):
            return "fedora"
        if file_exists("/etc/mandriva-release"):
            return "mandriva"
        if file_exists("/etc/mandrake-release"):
            return "mandrake"
        if file_exists("/etc/meego-release"):
            return "meego"
        if file_exists("/etc/arch-release"):
            return "arch"
        if file_exists("/etc/oracle-release"):
            return "oracle"
        if file_exists("/etc/vmware-release"):
            return "vmware"
        if file_exists("/etc/redhat-release"):
            dist = file_read("/etc/redhat-release").lower()
            if "centos" in dist:
                return "centos"
            # TODO: Add other exotic redhat based distributions
            else:
                return "redhat"
        if file_exists("/etc/SuSe-release"):
            dist = file_read("/etc/SuSe-release").lower()
            if "suse linux enterprise server" in dist:
                return "sles"
            if "suse linux enterprise desktop" in dist:
                return "sled"
            if "opensuse" in dist:
                return "opensuse"
            else:
                return "suse"
        if file_exists("/etc/slackware-release"):
            return "slackware"
        if file_exists("/etc/system-release"):
            return "amazon"
    else:
        return "unknown"

from mico.lib.core import network_address
from mico.lib.core import network_interfaces
@environ('ipaddr')
def _env_ipaddr():
    """Returns a dictionary with the IP address of the remote hosts,
    indexed by interface. For example:

    .. code-block:: python

        ips = env.cutom.ip_addr
        print ips['eth0']
    """
    ret = AttrLazyDict()
    for iface in network_interfaces():
        ret[iface] = network_address(iface)
    return ret

from mico.lib.core import network_nameservers
@environ('nameservers')
def _env_nameservers():
    """Returns the nameserver configured in the remote host.
    """
    return network_nameservers()

