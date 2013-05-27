Writing templates
-----------------

Templates are the base of mico. Mico by default looking for templates in
current working directory as well as ``/etc/mico`` and ``~/.config/mico``.

Template is a python file which can access to all mico builtins methods
(like ``@serial`` or ``@async`` decorators), and also functions in libraries
where imported.

To call a template just run mico with the template name as first argument.
Optionally you can specify a function to run, in the form::

  $ mico template:function

If not function specified, then use ``main`` function by default.

Here are a basic template for mico:

.. code-block:: python

    from mico.lib.aws import *
    from mico.lib.core import *

    def deploy(\*args):
        for host in args:
            host, domain = host.split('.', 1) \
                           if '.' in host \
                           else (host, 'localdomain')

            sg_test = sg_ensure(
                name        = "sg-test",
                description = "security group to test mico",
                rules = [
                    sg_rule(
                        protocol = "tcp",
                        source   = "0.0.0.0/0",
                        port     = "22"
                    ),
                    sg_rule(
                        protocol = "tcp",
                        source = "0.0.0.0/0",
                        port = "80"
                    )
                ]
            )

            instance = ec2_ensure(
                ami = "ami-3d4ff254",
                name = host,
                instance_type = "t1.micro",
                key_name = "root-us-east-virginia",
                security_groups = sg_test
           )


.. note:: You don't need to be worried about how to link EC2 instance with
    host where local commands will be executed. In previous example the
    *pkg_ensure* command will be executed rightly in the instance which has
    been created in the previous line with the *ec2_ensure* command.

    This works fine, because mico works sequentially for each task.

