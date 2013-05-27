#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""The local module provides functions to perform some actions in local
machine."""

import __builtin__

from hashlib import sha1
from jinja2 import Environment, FileSystemLoader

import mico

def local_content(src, var={}):
    """Read a file content (which is a jinja2 template), parser it using
    provided environment plus the global environment (the local one override
    the global one, and save the return in a remote file if file changes.

    :type src: string
    :param src: the path to local content file to be applied

    :type var: dict
    :param var: a dictionary to use as environment for template
    """

    jinja_env = Environment(loader=FileSystemLoader(mico.config_path))
    jinja_tpl = jinja_env.get_template(src)

    local_env = dict([ (k,v) for (k,v) in __builtin__.env.items() ])
    local_env.update(var)

    content = jinja_tpl.render(**local_env)
    return content

from mico.util.switch import Switcher
mode_local = Switcher.from_key("mode_local", True)

def is_local():
    """Return True if the execution is running in local host."""
    return mode_local.getValue("mode_local")

def is_remote():
    """Return True if the execution is running in remote host."""
    return not is_local()

import subprocess
from fabric import operations
from StringIO import StringIO

def run_local(command, sudo=False, shell=True, pty=True, combine_stderr=None):
    """Local implementation of fabric.api.run() using subprocess.

    .. note:: pty option exists for function signature compatibility and is
        ignored.
    """
    if combine_stderr is None:
        combine_stderr = env.combine_stderr

    # TODO: Pass the SUDO_PASSWORD variable to the command here
    if sudo:
        command = "sudo " + command

    mico.output.debug(command)

    stderr   = subprocess.STDOUT if combine_stderr else subprocess.PIPE
    process  = subprocess.Popen(command, shell=shell, stdout=subprocess.PIPE, stderr=stderr)
    out, err = process.communicate()

    # FIXME: Should stream the output, and only print it if fabric's properties allow it
    # print out
    # Wrap stdout string and add extra status attributes
    result = operations._AttributeString(out.rstrip('\n'))
    result.return_code = process.returncode
    result.succeeded   = process.returncode == 0
    result.failed      = not result.succeeded
    result.stderr      = StringIO(err)
    return result

