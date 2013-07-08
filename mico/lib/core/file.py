#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""The file core submodule provide a useful way to create, delete and manage
files in the remote and local host."""

import os
import base64
import hashlib
import tempfile
import __builtin__

from jinja2 import Environment, FileSystemLoader

import fabric

import mico.output
import mico.util.storage
revision_repo = mico.util.storage.RevisionStorage(
        os.path.join(mico.cache_path, __name__)
)

def file_attribs(location, mode=None, owner=None, group=None, recursive=False):
    """Updates the mode/owner/group for the remote file at the given
    location.
    """
    recursive = recursive and "-R " or ""
    _x = None
    if mode:
        _x = run('chmod %s %s "%s"' % (recursive, mode,  location))
        mico.output.info("set attributes for %s to %s" % (location, mode))
    if owner:
        _x = run('chown %s %s "%s"' % (recursive, owner, location))
        mico.output.info("set owner for %s to %s" % (location, owner))
    if group:
        _x = run('chgrp %s %s "%s"' % (recursive, group, location))
        mico.output.info("set group for %s to %s" % (location, group))

    return _x

from mico.lib.core.dir import dir_ensure

from mico.lib.core.local import *

def file_local_read(location):
    """Reads a *local* file from the given location, expanding '~' and
    shell variables.
    """
    with file(os.path.expandvars(os.path.expanduser(location)), "rb") as f:
        return f.read()

def file_read(location):
    """Reads the *remote* file at the given location.

    .. note:: We use base64 here to be sure to preserve the encoding
        (UNIX/DOC/MAC) of EOLs
    """
    with fabric.context_managers.settings(fabric.api.hide('stdout')):
        _exe = run('openssl base64 -in "%s"' % (location))
        if _exe.return_code == 0:
            return base64.b64decode(_exe)

def file_exists(location):
    """Tests if there is a *remote* file at the given location."""
    _exe = run("test -e '%s'" % (location), force=True)
    return _exe.return_code == 0

def file_is_file(location):
    _exe = run("test -f '%s'" % (location))
    return _exe.return_code == 0

def file_is_dir(location):
    _exe = run("test -d '%s'" % (location))
    return _exe.return_code == 0

def file_is_link(location):
    _exe = run("test -L '%s'" % (location))
    return _exe.return_code == 0

def file_attribs_get(location):
    """Return mode, owner, and group for remote path.
    Return mode, owner, and group if remote path exists, 'None'
    otherwise.
    """
    if file_exists(location):
        fs_check = run('stat %s %s' % (location, '--format="%a %U %G"'))
        if fs_check.return_code == 0:
            (mode, owner, group) = fs_check.split(' ')
            return {'mode': mode, 'owner': owner, 'group': group}
        else:
            return None
    else:
        return None

def file_md5(location):
    """Returns the MD5 sum (as a hex string) for the remote file at the given location.

    .. note::
        In some cases, sudo can output errors in here -- but the errors will
        appear before the result, so we simply split and get the last line to
        be on the safe side.
    """
    sig = run('md5sum "%s" | cut -d" " -f1' % (location))
    if sig.return_code == 0:
        return sig.split(os.linesep)[-1].strip()

def file_sha256(location):
    """Returns the SHA256 sum (as a hex string) for the remote file at the given location.

    .. note::
        In some cases, sudo can output errors in here -- but the errors will
        appear before the result, so we simply split and get the last line to
        be on the safe side.
    """
    sig = run('shasum -a 256 "%s" | cut -d" " -f1' % (location))
    if sig.return_code == 0:
        return sig.split(os.linesep)[-1].strip()

def file_write(location, content, mode=None, owner=None, group=None, check=True):
    """Writes the given content to the file at the given remote
    location, optionally setting mode/owner/group.
    """
    # FIXME: Big files are never transferred properly!
    # Gets the content signature and write it to a secure tempfile
    sig = hashlib.md5(content).hexdigest()
    fd, lpath = tempfile.mkstemp()

    # Save the content to local temporary file
    os.write(fd, content)
    # Upload the content if necessary
    if sig != file_md5(location):
        if is_local():
            run("cp '%s' '%s'"%(lpath,location))
        else:
            # FIXME: Put is not working properly, I often get stuff like:
            # Fatal error: sudo() encountered an error (return code 1) while executing 'mv "3dcf7213c3032c812769e7f355e657b2df06b687" "/etc/authbind/byport/80"'
            #fabric.operations.put(local_path, location, use_sudo=use_sudo)
            # Hides the output, which is especially important
            # See: http://unix.stackexchange.com/questions/22834/how-to-uncompress-zlib-data-in-unix
            result = run("echo '%s' | openssl base64 -A -d -out '%s'" % (base64.b64encode(content), location))
    # Remove the local temp file
    os.fsync(fd)
    os.close(fd)
    os.unlink(lpath)
    # Ensures that the signature matches
    if check:
        file_sig = file_md5(location)
        if file_sig != sig:
            raise ExecutionError("Signature for '%s' does not match: got %s, expects %s" % (location, repr(file_sig), repr(sig)))

    _x =  file_attribs(location, mode=mode, owner=owner, group=group)
    mico.output.info("created file %s" % (location, ))
    return _x

def file_ensure(location, mode=None, owner=None, group=None):
    """Updates the mode/owner/group for the remote file at the given
    location.
    """
    if file_exists(location):
        return file_attribs(location,mode=mode,owner=owner,group=group)
    else:
        return file_write(location,"",mode=mode,owner=owner,group=group)

def file_update(location, updater=lambda x:x):
    """Updates the content of the given by passing the existing
    content of the remote file at the given location to the 'updater'
    function.

    For instance, if you'd like to convert an existing file to all
    uppercase, simply do:

    >   file_update("/etc/myfile", lambda _:_.upper())
    """
    if not file_exists(location):
        raise ExecutionError("file does not exists")

    new_content = updater(file_read(location))
    _x = run("echo '%s' | openssl base64 -A -d -out '%s'" % (base64.b64encode(new_content), location))
    mico.output.info("updated %d bytes into file %s" % (len(new_content), location, ))
    return _x

def file_append(location, content, mode=None, owner=None, group=None):
    """Appends the given content to the remote file at the given
    location, optionally updating its mode/owner/group.
    """
    run('echo "%s" | openssl base64 -A -d >> "%s"' % (base64.b64encode(content), location))
    _x = file_attribs(location, mode, owner, group)
    mico.output.info("appended %d bytes into file %s" % (len(content), location, ))
    return _x

def file_unlink(path):
    """Unlink or remove a file"""
    if file_exists(path):
        _x = run("unlink '%s'" % (path))
        mico.output.info("removed file %s" % (location, ))
        return _x

def file_link(source, destination, symbolic=True, mode=None, owner=None, group=None):
    """Creates a (symbolic) link between source and destination on the remote host,
    optionally setting its mode/owner/group.
    """
    if file_exists(destination) and (not file_is_link(destination)):
        raise ExecutionError("Destination already exists and is not a link: %s" % (destination))

    # FIXME: Should resolve the link first before unlinking
    if file_is_link(destination):
        file_unlink(destination)
    if symbolic:
        run("ln -sf '%s' '%s'" % (source, destination))
    else:
        run("ln -f '%s' '%s'" % (source, destination))
    return file_attribs(destination, mode, owner, group)


def file_content(src, dst, env={}, mode=None, owner=None, group=None,
                check=True, override_mode=True, override_owner=True,
                override_group=True):
    """Read a file content (which is a jinja2 template), parser it using
    provided environment plus the global environment (the local one override
    the global one, and save the return in a remote file if file changes.

    :type src: string
    :param src: the path to local content file to be applied

    :type dst: string
    :param dst: the remote file path to be written

    :type env: dict
    :param env: a local environment to be passed to the content template, by
        default the entire global environment is passed, local values will
        be override the global ones.

    :type mode: int
    :param mode: the file mode use to save the file

    :type owner: string
    :param owner: the owner of the file

    :type group: string
    :param group: the group which owns the file

    :type check: bool
    :param check: if True (by default) check that file is created properly

    :type override_mode: bool
    :param override_mode: if True (by default) use the mode passed as
        argument even if file is already created in remote with another mode.

    :type override_owner: bool
    :param override_mode: if True (by default) use the owner passed as
        argument even if file is already created in remote with another
        owner.

    :type override_mode: bool
    :param override_mode: if True (by default) use the group passed as
        argument even if file is already created in remote with another
        group.
    """
    jinja_env = Environment(loader=FileSystemLoader(mico.config_path))
    jinja_tpl = jinja_env.get_template(src)

    local_env = dict([ (k,v) for (k,v) in __builtin__.env.items() ])
    local_env.update(env)

    content = jinja_tpl.render(**local_env)
    hash_content = hashlib.sha1(content).hexdigest()

    dir_ensure(os.path.dirname(dst), True, mode=mode, owner=owner,
            group=group)

    if file_exists(dst):
        original  = file_read(dst)
        orig_attr = file_attribs_get(dst)

        if override_mode and mode:
            orig_attr["mode"] = mode
        if override_owner and owner:
            orig_attr["owner"] = owner
        if override_group and group:
            orig_attr["group"] = group
    else:
        original  = ""
        orig_attr = { "mode":mode, "group":group, "owner":owner }

    hash_original = hashlib.sha1(original).hexdigest()
    _path = os.path.join(local_env["host_string"], dst.strip("/"))
    if hash_original != hash_content or _path not in revision_repo:
        revision_repo[_path] = original
        file_write(dst, content)
        file_attribs(dst, **orig_attr)

