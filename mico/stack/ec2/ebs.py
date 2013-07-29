#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""EBS stack provides functions to work with AWS EC2 volumes.
"""

import sys
import mico.output
from mico.lib.aws.ec2 import *

def ls(*args):
    """List volumes filtering with tag name, provided in arguments. Glob
    expressions are allowed in filters as multiple filters too, for
    example::

        mico ec2.ebs ls apaches-* test-*
    """
    for x in ebs_list(*args):
        mico.output.dump(x, layout=env.get("layout","vertical"))

def rm(*args):
    """Remove volumes which match with the volume id passed as argument.

        mico ec2.ebs rm vol-123456 vol-098765

    If volume is attached or something fails before to do the rm action, you
    need to set the *force* variable to Tue in the enviroment to force
    deletion, otherwise action will fail.
    """
    for x in args:
        try:
            if env.get("force",False):
                try:
                    ebs_detach(x, env.get("detach_force", None))
                except boto.exception.EC2ResponseError as e:
                    pass
            ebs_delete(x)
        except boto.exception.EC2ResponseError as e:
            mico.output.error("Unable to remove volume %s: %s"
                    % (x, e.error_message,))

def detach(*args):
    """Detach a number of volumes if attached.
    For example:

        mico ec2.ebs detach vol-12345
    """
    for x in args:
        ebs_detach(x, env.get("detach_force", None))

def main(*args):
    if len(args) > 0:
        fn = getattr(sys.modules[__name__],args[0])
        return fn(*args[1:])
    else:
        return ls()

