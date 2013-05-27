#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

import urllib2
import hashlib

import mico.output

def import_code(code, name, add_to_sys_modules=0):
    """Import dynamically generated code as a module. code is the
    object containing the code (a string, a file handle or an
    actual compiled code object, same types as accepted by an
    exec statement). The name is the name to give to the module,
    and the final argument says wheter to add it to sys.modules
    or not. If it is added, a subsequent import statement using
    name will return this module. If it is not added to sys.modules
    import will try to load it in the normal fashion.

    import foo

    is equivalent to

    foofile = open("/path/to/foo.py")
    foo = importCode(foofile,"foo",1)

    Returns a newly generated module.
    """
    import sys,imp

    module = imp.new_module(name)

    exec code in module.__dict__
    if add_to_sys_modules:
        sys.modules[name] = module

    return module


class Template(type(__builtins__)):
    @classmethod
    def load(cls, mod, fun=[]):
        if mod.startswith("http://") or mod.startswith("https://"):
            try:
                _mod = import_code(urllib2.urlopen(mod).read(),"_mico_dm_%s" % hashlib.sha1("mod").hexdigest(), True)
                mico.output.debug("loaded remote template: %s" % mod)
                mod = _mod
            except urllib2.HTTPError:
                raise ImportError("Unable to download template")
        else:
            mod = __import__(mod, globals(), locals(), fun, -1)
        if fun:
            fun = getattr(mod, fun[0])
        else:
            fun = None
        return (mod, fun)

