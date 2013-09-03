
#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""EC2 stack to handle actions over EC2 infrastructure.
"""

import sys
import mico.run
import mico.output

from mico.lib.aws.ec2 import *


__all__ = ["as", "ebs", "sg"]


def ls(*args):
    """List instances filtering with tag name, provided in arguments. Glob
    expressions are allowed in filters as multiple filters too, for
    example::

        mico ec2 ls apaches-* test-*
    """
    for x in ec2_list(*args):
        mico.output.dump(x, layout=env.get("layout", "vertical"))


def reboot(*args):
    """Reboot specified instances, for example::

        mico ec2 reboot apaches-* test-*
    """
    for x in ec2_list(*args):
        x.reboot()
        mico.output.info("Reboot instance: %s (%s)" % (x.name, x.id,))


def stop(*args):
    """Stop specified instances, for example::

        mico ec2 stop apaches-* test-*
    """
    for x in ec2_list(*args):
        x.stop()
        mico.output.info("Stop instance: %s (%s)" % (x.name, x.id,))


def start(*args):
    """Start specified instances, for example::

        mico ec2 start apaches-* test-*
    """
    for x in ec2_list(*args):
        x.start()
        mico.output.info("Start instance: %s (%s)" % (x.name, x.id,))


def terminate(*args):
    """Terminate specified instances, for example::

        mico ec2 terminate apaches-* test-*

    If termination protection is enabled, then *force* variable must be
    setted to True into the environment, otherwise terminate will fail.
    """
    for x in ec2_list(*args):
        try:
            if env.get("force", False):
                x.modify_attribute("disableApiTermination", False)
                mico.output.debug("Disabling termination protection for instance %s (%s)" % (x.name, x.id,))
            x.terminate()
            mico.output.info("Terminate instance: %s (%s)" % (x.name, x.id,))
        except boto.exception.EC2ResponseError as e:
            mico.output.error("Unable to terminate instance %s (%s): %s"
                    % (x.name, x.id, e.error_message,))


def run(*args):
    """Execute command over a number of hosts which match with specified Tag
    name provided as argument. Example::

        mico ec2 run 'apaches-*' service apache reload
    """
    env.host_label = {x.ip_address: x.name for x in ec2_list(args[0]) if x.ip_address is not None}
    env.roledefs['mico'] = [x for x in env.host_label]

    env.roles.append('mico')

    if len(env.roledefs['mico']) > 0:
        mico.run.run(" ".join(args[1:]))


def main(*args):
    if len(args) > 0:
        fn = getattr(sys.modules[__name__], args[0])
        return fn(*args[1:])
    else:
        return ls()

# Alias definitions
rm = terminate
halt = stop
shutdown = stop
restart = reboot

