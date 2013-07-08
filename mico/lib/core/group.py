#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""The group core submodule provide a useful way to create, delete and manage
groups in the remote host."""

import mico.output

def group_create(name, gid=None):
    """Creates a group with the given name, and optionally given gid.
    """
    _x = run("groupadd %s '%s'" % ( ("-g '%s'" % gid) if gid else "", name ))
    mico.output.info("created group %s" % name)
    return _x

def group_exists(name):
    """Checks if there is a group defined with the given name.

    :returns: a dict with fields name (name of the group), gid (GID of the
        group), members (a list with members of the group) or None if the
        group does not exists.
    """
    group_data = run("cat /etc/group | egrep '^%s:'" % (name), force=True)
    if group_data:
        name, _, gid, members = group_data.split(":", 4)
        return dict(name=name, gid=gid,
                    members=tuple(m.strip() for m in members.split(",")))
    else:
        return None

def group_remove(name):
    """Remove a group which match with specified name.
    """
    if group_exists(name):
        _x = run("groupdel '%s'" % name)
        mico.output.info("removed group %s" % name)
        return _x
    else:
        mico.output.debug("skip removing unexistant group %s" % name)


def group_ensure(name, gid=None):
    """Ensures that the group with the given name (and optional gid)
    exists.
    """
    d = group_exists(name)
    if not d:
        return group_create(name, gid)
    else:
        if gid != None and d.get("gid") != gid:
            _x = run("groupmod -g %s '%s'" % (gid, name))
            mico.output.info("changed GID for group %s to %d" % (name, gid,))
            return _x

def group_user_exists(group, user):
    """Checks if the given user is a member of the given group. It
    will return 'False' if the group does not exist.
    """
    d = group_exists(group)
    if d is None:
        return False
    else:
        return user in d["members"]

def group_user_add(group, user):
    """Adds the given user/list of users to the given group/groups.
    """
    if not group_exists(group):
        raise ExecutionError("group %s does not exists" % group)

    if not group_user_exists(group, user):
        _x = run("usermod -a -G '%s' '%s'" % (group, user))
        mico.output.info("added user %s into group %s" % (user, group,))
        return _x

def group_user_ensure(group, user):
    """Ensure that a given user is a member of a given group.
    """
    d = group_check(group)
    if user not in d["members"]:
        return group_user_add(group, user)

def group_user_del(group, user):
        """Remove the given user from the given group.
        """
        if not group_check(group):
            raise ExecutionError("group %s does not exists" % group)

        if group_user_exists(group, user):
            group_for_user = run("cat /etc/group | egrep -v '^%s:' | grep '%s' | awk -F':' '{print $1}' | grep -v %s" % (group, user, user), force=True)
            if group_for_user.return_code == 0:
                group_for_user = group_for_user.splitlines()
                if group_for_user:
                    _x = run("usermod -G '%s' '%s'" % (",".join(group_for_user), user))
                    mico.output.info("removed user %s from group %s" % (user,group,))
                    return _x


