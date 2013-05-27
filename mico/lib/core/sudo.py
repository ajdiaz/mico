#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""The sudo core submodule provide a useful way to execute remote commands
in sudo mode."""

from mico.util.switch import Switcher

ENV_KEY_SUDO_PASSWORD = "sudo_password"
ENV_KEY_SUDO_MODE     = "sudo_mode"

def sudo_password(password=None):
    """Set the password to be used with sudo

    :type password: str
    :param password: the password to be used with sudo if required. If not
        set then try to use the defined one in the mico environment as
        ``sudo_password``, if set to empty string, then never use password.
    """
    if password is None:
        return env.get(ENV_KEY_SUDO_PASSWORD, None)
    else:
        if not password:
            del env[ENV_KEY_SUDO_PASSWORD]
        else:
            env[ENV_KEY_SUDO_PASSWORD] = password

mode_sudo = Switcher.from_key(ENV_KEY_SUDO_MODE, True)

def is_sudo():
    """Return true if the current execution mode is sudo-enabled"""
    return mode_sudo.getValue(ENV_KEY_SUDO_MODE)

def sudo(*args, **kwargs):
    """A wrapper to Fabric's run/sudo commands, using the
    mode_sudo global to tell whether the command should be run as
    regular user or sudo.
    """
    with mode_sudo():
        return run(*args, **kwargs)

