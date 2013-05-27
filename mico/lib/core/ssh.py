#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""The ssh core submodule provide a useful way to create, delete and manage
ssh keys in remote hosts"""

import os

import mico.output
from mico.lib.core.dir import dir_ensure
from mico.lib.core.sudo import mode_sudo
from mico.lib.core.user import user_exists
from mico.lib.core.file import file_attribs, file_exists, \
                               file_read, file_append, file_write

def ssh_keygen(user, key_type="rsa"):
    """Generates a pair of ssh keys in the user's home .ssh directory.
    """
    d = user_exists(user)
    if not d:
        raise ExecutionError("user '%s' does not exists" % user)
    elif "home" not in d:
        raise ExecutionError("user '%s' has not declared path" % user)
    else:
        key_file = os.path.join(d["home"], ".ssh/id_%s.pub" % key_type)
        if not file_exists(key_file):
            dir_ensure(os.path.join(d["home"], ".ssh/"), mode="0700", owner=user)
            _x = run("ssh-keygen -q -t %s -f '%s/.ssh/id_%s' -N ''" % (
                key_type,
                d["home"],
                key_type
            ))
            mico.output.info("created ssh-key for user %s" % user)
            if _x.return_code == 0:
                _x = file_attribs(os.path.join(d["home"],".ssh/id_%s" % key_type), owner=user)
                if _x.return_code == 0:
                    return file_attribs(os.path.join(d["home"],".ssh/id_%s.pub" % key_type), owner=user)
                else:
                    return _x
            else:
                return _x

def ssh_authorize(user, key):
    """Adds the given key to the '.ssh/authorized_keys' for the given
    user."""
    u = user_exists(user)
    if not u:
        raise ExecutionError("user '%s' does not exists" % user)
    elif "home" not in u:
        raise ExecutionError("user '%s' has not declared path" % user)
    else:
        key_file = os.path.join(u["home"], ".ssh/authorized_keys")
        key = key.strip(os.linesep) + os.linesep

        if file_exists(key_file):
            data = file_read(key_file)
            if data.find(key[:-1]) == -1:
                _x = file_append(key_file, key)
            else:
                _x = data
            mico.output.info("key %s added to user %s" % (key.split()[2], user,))
            return _x
        else:
            _x = dir_ensure(os.path.dirname(key_file), owner=user, mode="700")
            if _x.return_code == 0:
                _x = file_write(key_file, key, owner=user, mode="600")
                if _x.return_code == 0:
                    _x = file_attribs(key_file, owner=user, mode="600")
            mico.output.info("key %s added to user %s" % (key.split()[2], user,))
            return _x

