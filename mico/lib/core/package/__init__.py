#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""The package core submodule provides basic actions to install packages and
package repositories into a host using a properly standard way."""

import mico.lib.core.package.apt
import mico.lib.core.package.yum

class UnknowDistributionError(Exception):
    """Model an error related with distribution of the operating system
    installed in the remote machine."""

def repository_ensure(repository, key=None):
    """Ensures that a repository is installed in the remote host. This
    function works as a wrapper over installed backend engines for package
    mangling, using current installed distribution in your machine."""

    operating_system = env.custom.operating_system

    if operating_system == "debian" or \
       operating_system == "ubuntu":
           return mico.lib.core.package.apt.repository_ensure(repository, key)

    if operating_system == "centos" or \
       operating_system == "redhat" or \
       operating_system == "fedora":
           return mico.lib.core.package.yum.repository_ensure(repository)


def package_ensure(*args, **kwargs):
    operating_system = env.custom.operating_system

    if operating_system == "debian" or \
       operating_system == "ubuntu":
           return mico.lib.core.package.apt.package_ensure(*args, **kwargs)

    if operating_system == "centos" or \
       operating_system == "redhat" or \
       operating_system == "fedora":
           return mico.lib.core.package.yum.package_ensure(*args, **kwargs)


def package_update(*args, **kwargs):
    operating_system = env.custom.operating_system

    if operating_system == "debian" or \
       operating_system == "ubuntu":
           return mico.lib.core.package.apt.package_update(*args, **kwargs)

    if operating_system == "centos" or \
       operating_system == "redhat" or \
       operating_system == "fedora":
           return mico.lib.core.package.yum.package_update(*args, **kwargs)


def package_upgrade(*args, **kwargs):
    operating_system = env.custom.operating_system

    if operating_system == "debian" or \
       operating_system == "ubuntu":
           return mico.lib.core.package.apt.package_upgrade(*args, **kwargs)

    if operating_system == "centos" or \
       operating_system == "redhat" or \
       operating_system == "fedora":
           return mico.lib.core.package.yum.package_upgrade(*args, **kwargs)


def package_remove(*args, **kwargs):
    operating_system = env.custom.operating_system

    if operating_system == "debian" or \
       operating_system == "ubuntu":
           return mico.lib.core.package.apt.package_remove(*args, **kwargs)

    if operating_system == "centos" or \
       operating_system == "redhat" or \
       operating_system == "fedora":
           return mico.lib.core.package.yum.package_remove(*args, **kwargs)

