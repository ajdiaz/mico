#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

import os
import sys
import inspect

import mico
from mico.lib.core.local import is_local

intros = [
        "the monkey army for the cloud",
        "just see! a monkey flying in the cloud",
        "uuuh uhuh uhuhuhuhu uh uh uh!",
        "the monkey driven cloud management",
        "oh no! monkys are learning to fly!",
        "take your stinking paws off me, you dammed dirty ape!"
]

monkey = """
             .--.  .-"     "-.  .--.
            / .. \/  .-. .-.  \/ .. \\
           | |  '|  /   Y   \  |'  | |
           | \\   \\  \\ 0 | 0 /  /   / |
            \ '- ,\.-"`` ``"-./, -' /
             `'-' /_   ^ ^   _\\ '-'`
             .--'|  \._   _./  |'--.
           /`    \   \ `~` /   /    `\\ 
          /       '._ '---' _.'       \\
         /           '~---~'   |       \\
        /        _.             \\       \\
       /   .'-./`/        .'~'-.|\\       \\
      /   /    `\:       /      `\'.      \\
     /   |       ;      |         '.`;    /
     \   \       ;      \\           \/   /
      '.  \      ;       \\       \   `  /
        '._'.     \       '.      |   ;/_
          /__>     '.       \\_ _ _/   ,  '--.
        .'   '.   .-~~~~~-. /     |--'`~~-.  \\
       // / .---'/  .-~~-._/ / / /---..__.'  /
      ((_(_/    /  /      (_(_(_(---.__    .'
                | |     _              `~~`
                | |     \\'.
                 \ '....' |
                  '.,___.'
"""

prompt_usr = os.environ.get("MICO_PS1", None) or "[0;1mmico[1;34m:[0;0m "
prompt_err = os.environ.get("MICO_PS2", None) or "[31;1mmico[0;1m:[0;0m "
prompt_inf = os.environ.get("MICO_PS3", None) or "[33;1mmico[0;1m:[0;0m "
prompt_msg = os.environ.get("MICO_PS4", None) or "[34;1mmico[0;1m:[0;0m "
prompt_dbg = os.environ.get("MICO_PS4", None) or "[30;1mmico[0;1m:[0;0m "

env.loglevel = set([ "abort", "error", "warn", "info" ])

def abort(message):
    if "abort" in env.loglevel:
        _h = env["host_string"] or ("local" if is_local() else "cloud")
        print >> sys.stderr, "%s[0;1m%s:[0;0m %s: %s" % (prompt_err,
                _h, inspect.stack()[1][3], message)

def error(message,func=None,exception=None,stdout=None,stderr=None):
    if "error" in env.loglevel:
        _h = env["host_string"] or ("local" if is_local() else "cloud")
        print >> sys.stderr, "%s[0;1m%s:[0;0m %s: %s" % (prompt_err,
                _h, inspect.stack()[1][3], exception or message)

def warn(message):
    if "warn" in env.loglevel:
        _h = env["host_string"] or ("local" if is_local() else "cloud")
        print >> sys.stderr, "%s[0;1m%s:[0;0m %s: %s" % (prompt_inf,
                _h, inspect.stack()[1][3], message)

def puts(text, show_prefix=None, end='\n', flush=False):
    if "info" in env.loglevel:
        _h = env["host_string"] or ("local" if is_local() else "cloud")
        print >> sys.stderr, "%s[0;1m%s:[0;0m %s: %s" % (prompt_inf,
                _h, inspect.stack()[1][3], text)

def info(message):
    if "info" in env.loglevel:
        _h = env["host_string"] or ("local" if is_local() else "cloud")
        print >> sys.stdout, "%s[0;1m%s:[0;0m %s: %s" % (prompt_msg,
                _h, inspect.stack()[1][3], message)

def debug(message):
    if "debug" in env.loglevel:
        _h = env["host_string"] or ("local" if is_local() else "cloud")
        print >> sys.stdout, "%s[0;1m%s:[0;0m %s: %s" % (prompt_dbg,
                _h, inspect.stack()[1][3], message)

def mute(*args, **kwargs):
    pass

from fabric.state import output
# XXX Supress some fabric messages, actually fabric message API is not very
# useful nor well designed.
output["debug"] =  False
output["running"] = False
output["stderr"] = False
output["stdout"] = False
output["status"] = False

import fabric.tasks
import fabric.utils
import fabric.operations
# XXX fabric monkey patching for message output
fabric.operations.abort = fabric.utils.abort = fabric.tasks.abort = abort
fabric.operations.error = fabric.utils.error = fabric.tasks.error = mute
fabric.operations.warn  = fabric.utils.warn  = fabric.tasks.warn  = mute
fabric.operations.puts  = fabric.utils.puts  = fabric.utils.puts  = mute
fabric.operations.fastprint = fabric.utils.fastprint  = fabric.utils.fastprint  = puts

