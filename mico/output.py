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

dump_keys = [
        "created_time", "default_cooldown", "desired_capacity", "min_size",
        "max_size", "health_check_period", "health_check_type",
        "launch_config_name", 'reason', 'description','endElement', 'end_time',
        'progress', 'startElement', 'start_time', 'status_code',
        'adjustment_type', 'alarms', 'as_name', 'cooldown',
        'min_adjustment_step','scaling_adjustment', "status",
        'comparison', 'dimensions', 'disable_actions', 'create_time',
        'enable_actions', 'evaluation_periods', 'zone',
        'last_updated','metric', 'instance_id', 'id',
        'period', 'set_state', 'autoscaling_group', 'snapshot_id',
        'state_reason', 'state_value', 'statistic', 'type',
        'threshold', 'total_instances', 'device', 'size',
        '_state', 'root_device_type', 'instance_type',
        'image_id', '_placement', 'secgroups', 'ip_address',
        'ttl', 'resource_records', 'launch_time'
]

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
    return message

def error(message,func=None,exception=None,stdout=None,stderr=None):
    if "error" in env.loglevel:
        _h = env["host_string"] or ("local" if is_local() else "cloud")
        print >> sys.stderr, "%s[0;1m%s:[0;0m %s: %s" % (prompt_err,
                _h, inspect.stack()[1][3], exception or message)
    return message

def warn(message):
    if "warn" in env.loglevel:
        _h = env["host_string"] or ("local" if is_local() else "cloud")
        print >> sys.stderr, "%s[0;1m%s:[0;0m %s: %s" % (prompt_inf,
                _h, inspect.stack()[1][3], message)
    return message

def puts(text, show_prefix=None, end='\n', flush=False):
    if "info" in env.loglevel:
        _h = env["host_string"] or ("local" if is_local() else "cloud")
        print >> sys.stderr, "%s[0;1m%s:[0;0m %s: %s" % (prompt_inf,
                _h, inspect.stack()[1][3], text)
    return text

def info(message):
    if "info" in env.loglevel:
        _h = env["host_string"] or ("local" if is_local() else "cloud")
        print >> sys.stdout, "%s[0;1m%s:[0;0m %s: %s" % (prompt_msg,
                _h, inspect.stack()[1][3], message)
    return message

def debug(message):
    if "debug" in env.loglevel:
        _h = env["host_string"] or ("local" if is_local() else "cloud")
        print >> sys.stdout, "%s[0;1m%s:[0;0m %s: %s" % (prompt_dbg,
                _h, inspect.stack()[1][3], message)
    return message

def mute(*args, **kwargs):
    pass

def _vars(obj):
    """Internal emulation for builtin var. Not all boto objects provides
    __dict__ function.
    """

    #if hasattr(obj, "__dict__"):
    #    return vars(obj)

    return { k.strip("_"): getattr(obj,k) for k in filter(lambda
        x:not hasattr(getattr(obj,x),"__call__") and not x.startswith("__"), dir(obj)) }

def _str(obj):
    if hasattr(obj, "name"):
        return obj.name
    elif hasattr(obj, "id"):
        return obj.id
    elif hasattr(obj, "volume_id"):
        return obj.volume_id
    else:
        return str(obj)

def dump(obj, layout="horizontal", color=True):
    if color:
        s = "[33;1m%s[0;0m:" % getattr(obj, "name","None")
    else:
        s = "%s:" % getattr(obj, "name","None")

    v = _vars(obj)
    for key in v:
        if key in dump_keys or "debug" in env.loglevel:
            if v[key] is None:
                continue
            if isinstance(v[key],list):
                _val = ", ".join(map(_str,v[key]))
            elif isinstance(v[key], dict):
                _val = "{ "
                _val += ", ".join(map(lambda x:"%s:%s" % (x[0], _str(x[1]),), v[key].items()))
                _val += " }"
            else:
                _val = v[key]
            if not str(_val).strip():
                continue
            if layout == "vertical":
                s += "\n  "
            if color:
                s+=" %s = [0;1m%s[0;0m" % (key, _val)
            else:
                s+=" %s = %s" % (key, _val)

    if layout == "vertical":
        s+="\n"

    print >> sys.stdout, s


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

