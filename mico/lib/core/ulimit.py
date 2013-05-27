#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""The ulimit core submodule provide a useful way to manage system
ulimits."""

def ulimit_ensure(limits):
    """Ensure user limits.

    Example::

        ulimit_ensure("@root hard nproc 1024")
        ulimit_ensure([
            "@root hard nproc 1024",
            "@root soft nproc 1024"
        ])
    """
    if isinstance(limits, str):
        limits = limits.split("\n")

    # Remove extra spaces
    limits = map(lambda x:' '.join(x.split()), limits)

    for limit in limits:
        _x = run("sed 's:[ \\t][ \\t]*: :g' /etc/security/limits.conf " + \
                 "| grep '%s' || ( echo '%s' >> /etc/security/limits.conf; )" % (limit,limit,))

