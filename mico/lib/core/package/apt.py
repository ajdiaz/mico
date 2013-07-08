#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""The package yum package core submodule provides basic actions to install
packages and package repositories into a host using yum utility."""

import hashlib

def repository_ensure(repository, key):
    """Ensure that an APT repository exists.
    """
    if key is not None:
        run("curl %s | apt-key add -" % key)

    return run("echo '%s' > /etc/apt/sources.list.d/%s.list" % (
        repository,
        hashlib.sha1(repository).hexdigest(),
    ))

def package_update(package=None):
    """Update the package list or a package list referer a package passed as
    argument using APT tools.
    """
    if package is None:
        return run("apt-get --yes update")
    else:
        if type(package) in (list, tuple):
            package = " ".join(package)
        return run('DEBIAN_FRONTEND=noninteractive apt-get --yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade %s' % (package))

def package_upgrade(distupgrade=False):
    """Upgrade the system, or upgrade the distribution.

    :param distupgrade: when True, upgrade the distribution (False by
        default).
    """
    if distupgrade:
        return run('DEBIAN_FRONTEND=noninteractive apt-get --yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" dist-upgrade')
    else:
        return run('DEBIAN_FRONTEND=noninteractive apt-get --yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade')

def package_install(package, update=False):
    """Install a package using APT tool.

    :type package: str
    :param package: the package name to be installed

    :type update: bool
    :param update: when True, performs an update before (False by default).
    """
    if update:
        _x = run('DEBIAN_FRONTEND=noninteractive apt-get --yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" update')
        if _x.return_code != 0:
            raise ExecutionError("Unable to update, but required")

    if type(package) in (list, tuple):
        package = " ".join(package)

    return run("DEBIAN_FRONTEND=noninteractive apt-get --yes install %s" % (package))

def package_ensure(package, update=False):
    """Ensure apt packages are installed.

    :type package: str
    :param package: the package name to ensure

    :type update: bool
    :param update: when True performs an update before (False by default).
    """
    if not isinstance(package, basestring):
        package = " ".join(package)
    status = run("dpkg-query -W -f='${Status} ' %s ; true" % package)
    if ('No packages found' in status) or ('not-installed' in status) or ("installed" not in status):
        return package_install(package)
    else:
        if update:
            return package_update(package)
        return status

def package_clean(package=None):
    """Clean APT cache.

    :type package: str or list or tuple
    :param package: the package name to be clean.
    """
    if type(package) in (list, tuple):
        package = " ".join(package)
    return run("DEBIAN_FRONTEND=noninteractive apt-get -y --purge remove '%s'" % package)

def package_remove(package, autoclean=False):
    """Remove APT package.

    :type package: str
    :param package: the package to be removed

    :type autoclean: bool
    :param autoclean: If set (False by default) execute autoclean afte
        remove.
    """
    _x = run('DEBIAN_FRONTEND=noninteractive apt-get --yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" remove "%s"' % package)
    if _x.return_code == 0:
        if autoclean:
            return run('apt-get --yes autoclean')
    return _x



