#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""Queues are using to enqueue some actions which will be performed after
a task execution."""

from Queue import Queue

def put(action, parameters=()):
    """Enqueue one action with action parameters in environment"""

    if "mico_queue" in env:
        env["mico_queue"].put((action,parameters))
    else:
        env["mico_queue"] = Queue()
        env["mico_queue"].put((action,parameters))


def run():
    """Run enqueued actions"""
    if "mico_queue" in env:
        ret = []
        q = env["mico_queue"]
        while not q.empty():
            action, parameters = q.get()
            ret.append(action(*parameters))
        return ret
    return []


def get():
    """Get an element of the queue"""
    if "mico_queue" in env:
        q = env["mico_queue"]
        return q.get()

