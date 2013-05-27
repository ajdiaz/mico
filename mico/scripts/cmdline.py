#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

import os
import sys
import cmd
import shlex
import random
import pkgutil

import mico
import mico.fifo
import mico.util
import mico.hook
import mico.output

from mico.template import Template

class MicoCmdline(cmd.Cmd):
    """The command line console which will be invoked from mico script."""

    template_path = [
            "templates",
            "data",
            "content",
            "files",
            "sources"
    ]
    ruler     = '-'
    prompt    = mico.output.prompt_usr
    intro     = mico.output.prompt_msg + random.choice(mico.output.intros)

    def complete(self, text, state):
        "Return a list of completion options for console."

        options =  [i for i in map(lambda x:x[3:], filter(lambda x:x.startswith("do_"), dir(self) )) if i.startswith(text) if i != "EOF" ]
        options += [i for j in map(pkgutil.iter_modules, mico.config_path) for _,i,_ in j]

        if state < len(options):
            return options[state]
        else:
            return None

    def emptyline(self):
        pass

    def do_set(self, args):
        "Set an environment variable, in teh form variable=value"
        if "=" in args:
            args = args.split("=")
            try:
                eval("env.__setitem__('%s','%s')" % ( args[0], " ".join(args[1:]) ))
            except Exception, e:
                mico.output.error("invalid evaluation: %s" % e)
        else:
            mico.output.error("invalid syntax, required var=value")


    def do_host(self, host=[]):
        "Set hosts where command must run."

        if host:
            if "," in host:
                host = host.split(",")
            else:
                host = [ host ]

            env.hosts = host

    def do_env(self, args):
        "Print current environment."
        if args:
            if " " in args:
                args = split(" ")
            else:
                args = [ args ]

        for key in env:
            if not args or key in args:
                mico.output.puts("%-20s = %s" % ( key, env[key] ) )


    def do_EOF(self, *args):
        "Exits the shell, also works by pressing C-D."
        return True
    do_exit = do_EOF

    def do_peanut(self, *args):
        print mico.output.monkey

    def do_help(self, arg):
        'List available commands with "help" or detailed help with "help cmd"'
        if arg:
            # XXX check arg syntax
            try:
                func = getattr(self, 'help_' + arg)
            except AttributeError:
                try:
                    doc=getattr(self, 'do_' + arg).__doc__
                    if doc:
                        self.stdout.write("%s\n"%str(doc))
                        return
                except AttributeError:
                    pass
                self.stdout.write("%s\n"%str(self.nohelp % (arg,)))
                return
            func()
        else:
            names = self.get_names()
            cmds_doc = []
            cmds_undoc = []
            help = {}
            for name in names:
                if name[:5] == 'help_':
                    help[name[5:]]=1
            names.sort()
            # There can be duplicates if routines overridden
            prevname = ''
            for name in names:
                if name[:3] == 'do_':
                    if name == prevname:
                        continue
                    prevname = name
                    cmd=name[3:]
                    if cmd in help:
                        cmds_doc.append(cmd)
                        del help[cmd]
                    elif getattr(self, name).__doc__:
                        cmds_doc.append(cmd)
                    else:
                        cmds_undoc.append(cmd)

            for cmd in cmds_doc:
                print "%-15s%-s" % (cmd, getattr(self, "do_%s" % cmd).__doc__)



    def default(self, args):
        lexer = shlex.shlex(args)
        lexer.wordchars += "?*:/%&.-="
        lexer = tuple([ x for x in lexer ])

        mod, fun = lexer[0], ["main"]

        try:
            mod, fun = Template.load(mod, fun)
            if not mod.__name__.startswith("_mico_dm_"):
                mico.config_path.append(os.path.dirname(mod.__file__))
                for path in self.template_path:
                    mico.config_path.append(os.path.join(os.path.dirname(mod.__file__), path))
        except ImportError, e:
            mico.output.error("template '%s' not found: %s." % (mod,e,))
        except AttributeError, e:
            mico.output.error("function '%s' not found in template '%s': %s" % ( fun[0], mod, e, ))
        else:
            mico.execute(fun, *tuple(lexer[1:]))





def main():
    """Entrypoint for mico cmdline client."""
    import argparse

    cmdopt = argparse.ArgumentParser(
            description="mico: %s" % random.choice(mico.output.intros),
            epilog="©2012  Andrés J. Díaz <ajdiaz@connectical.com>")

    cmdopt.add_argument("-e", "--env", action="append",
                                      dest="env",
                                      help="set environment variable",
                                      type=str,
                                      default=[])
    cmdopt.add_argument("-H", "--host", action="append",
                                      dest="host",
                                      help="set host to target",
                                      type=str,
                                      default=[])
    cmdopt.add_argument("-R", "--region", action="store",
                                      dest="region",
                                      help="set EC2 region to work on",
                                      type=str,
                                      default="us-east-1")

    cmdopt.add_argument("-v", "--verbose", action="store_true",
                                      dest="verbose",
                                      help="be verbose",
                                      default=False)


    cmdopt.add_argument("template",
                        nargs='*',
                        default=None,
                        help="The template:function to execute or an internal command")

    args = cmdopt.parse_args()

    try:
        cmdlne = MicoCmdline()
        cmdlne.preloop()

        for opt in args.env:
            cmdlne.do_set(opt)

        for host in args.host:
            cmdlne.do_host(host)

        if args.verbose:
            env.loglevel.add("debug")

        env.ec2_region = args.region

        if len(args.template) == 0:
            cmdlne.cmdloop()
        else:
            cmdlne.onecmd(" ".join(args.template))
    except Exception, e:
        if "debug" in env.loglevel:
            raise e
        mico.output.error("unexpected error: %s: %s" % (e.__class__.__name__ ,e))

