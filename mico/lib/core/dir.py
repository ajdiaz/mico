#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""The dir core submodule provide a useful way to create, delete and manage
directories in the remote host."""

import mico.output

def dir_attribs(location, mode=None, owner=None, group=None, recursive=False):
    """Updates the mode/owner/group for the given remote directory.
    """
    from mico.lib.core.file import file_attribs
    return file_attribs(location, mode=mode, owner=owner, group=group, recursive=recursive)

def dir_exists(location):
    """Tells if there is a remote directory at the given location.
    """
    return (run("test -d '%s'" % location, force=True).return_code == 0)

def dir_remove(location, recursive=True):
    """Removes a directory
    """
    if dir_exists(location):
        _x = run("rm -%sf '%s'" % (recursive and "-r" or "", location))
        mico.output.info("removed directory %s" % location)
        return _x

def dir_ensure(location, recursive=True, mode=None, owner=None, group=None):
    """Ensures that there is a remote directory at the given location,
    optionally updating its mode/owner/group.

    If we are not updating the owner/group then this can be done as a single
    ssh call, so use that method, otherwise set owner/group after creation.
    """
    _x = None
    if not dir_exists(location):
        _x = run("mkdir %s '%s'" % (recursive and "-p" or "", location))
        if _x.return_code != 0:
            mico.output.error("unable to create directory %s" % location)
            return
        else:
            mico.output.info("created directory %s" % location)

    if owner or group or mode:
        return dir_attribs(location, owner=owner, group=group, mode=mode, recursive=recursive)
    else:
        return _x


