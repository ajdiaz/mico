#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""The service core submodule provide a useful way to execute service
actions."""

from fabric.api import hide
from fabric.api import settings

import mico.output
from mico.lib.core.sudo import sudo as mico_sudo

service_string = "service %(service)s %(action)s"

import mico.hook

def service_is_running(service):
    """Check if a service is running."""
    with settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
        res = mico_sudo(service_string % {
            "service": service,
            "action": "status"
        }, force=True)
        return res.succeeded

def service_ensure(service):
    """Ensure that a service is running."""
    if not service_is_running(service):
        return service_start(service)

def service_start(service):
    """Start a system service."""
    mico.hook.add_post_hook(mico_sudo, (service_string % {
        "service": service,
        "action": "start"
    },))
    mico.output.info("service %s enqueued to start" % service)

def service_stop(service):
    """Stop a system service."""
    mico.hook.add_post_hook(mico_sudo, (service_string % {
        "service": service,
        "action": "restart"
    },))
    mico.output.info("service %s enqueued to stop" % service)

def service_restart(service):
    """Restart a system service."""
    mico.hook.add_post_hook(mico_sudo, (service_string % {
        "service": service,
        "action":  "restart"
    },))
    mico.output.info("service %s enqueued to restart" % service)

def service_reload(service):
    """Reload a system service (when available)."""
    mico.hook.add_post_hook(mico_sudo, (service_string % {
        "service": service,
        "action":  "reload"
    },))
    mico.output.info("service %s enqueued to reload" % service)

def service_add_boot(service):
    """Add a service into the boot pipeline."""
    if env.custom.operating_system == "ubuntu" or \
       env.custom.operating_system == "debian":
           _x = mico_sudo("update-rc.d %s defaults" % service)
    if env.custom.operating_system == "redhat" or \
       env.custom.operating_system == "centos" or \
       env.custom.operating_system == "fedora":
           _x = mico_sudo("chkconfig '%s' on" % service)
    mico.output.info("service %s added to booting services" % service)
    return _x

def service_del_boot(service):
    """Remove a service from the boot pipeline."""
    if env.custom.operating_system == "ubuntu" or \
       env.custom.operating_system == "debian":
           _x = mico_sudo("update-rc.d -f %s remove" % service)
    if env.custom.operating_system == "redhat" or \
       env.custom.operating_system == "centos" or \
       env.custom.operating_system == "fedora":
           _x = mico_sudo("chkconfig '%s' off" % service)
    mico.output.info("service %s removed to booting services" % service)
    return _x

def service_ensure_boot(service):
    """Ensure that a service will be started on boot."""
    return service_add_boot(service)

