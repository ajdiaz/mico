#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

import __builtin__
from fabric.api import env
__builtin__.env = env

from mico.util.dicts import AutoCreatedLazyDict
__builtin__.env.custom = AutoCreatedLazyDict(env)

import sys

import mico.run
import mico.path
import mico.hook
import mico.environ
import mico.decorators


sys.path.extend(mico.path.get_library_path())


__builtin__.async = mico.decorators.async
__builtin__.serial = mico.decorators.serial
__builtin__.parallel = mico.decorators.parallel
__builtin__.sync = mico.decorators.sync
__builtin__.lock = mico.decorators.lock
__builtin__.run_local = mico.run.run_local
__builtin__.run = mico.run.run
__builtin__.execute = mico.run.execute

# XXX: Evaluate if storage has sense in environ
#__builtin__.env.storage = FileStorage(mico.path.get_cache_path())


