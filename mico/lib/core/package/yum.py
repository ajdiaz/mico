#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""The package yum package core submodule provides basic actions to install
packages and package repositories into a host using yum utility.
"""

def repository_ensure(repository):
    """Ensure that a yum repo is present.
    """
    raise Exception("Not implemented for Yum")

def package_upgrade():
    """Upgrade (update) yum cache.
    """
    return run("yum -y update")[0]

def package_update(package=None):
    """Upgrade a package.

    :type package: str or list or tuple
    :param pagage: the package(s) name to be updated or None for all.
    """
    if package == None:
        return run("yum -y update")[0]
    else:
        if type(package) in (list, tuple):
            package = " ".join(package)
        return run("yum -y upgrade " + package)[0]

def package_install(package, update=False):
    """Install a package

    :type package: str
    :param package: the package to be installed.


    :type update: bool
    :param update: if set to True (by default False), update cache first.
    """
    if update:
        _x = run("yum -y update")[0]
        if _x.return_code != 0:
            raise ExecutionError("Unable to update")

    if type(package) in (list, tuple):
        package = " ".join(package)
    return run("yum -y install %s" % (package))[0]

def package_remove(package, autoclean=False):
    """Remove YUM package.

    :type package: str
    :param package: the package to be removed

    :type autoclean: bool
    :param autoclean: If set (False by default) execute autoclean after
        remove (not work with yum).
    """
    _x = run("yum remove '%s'" % package)[0]
    if _x.return_code == 0:
        if autoclean:
            raise NotImplementedError("autoclean is not implemented in yum")
    return _x


