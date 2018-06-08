Mico: a monkey in the cloud
===========================

Mico is a tool-toy to manage a number of hosts deployed in cloud services
(currently only support Amazon AWS), and also allows you to deploy new hosts
with specified template or create autoscaling groups and manage them easily.

.. image:: https://img.shields.io/pypi/v/mico.svg
    :target: https://crate.io/packages/mico/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/dm/mico.svg
    :target: https://crate.io/packages/mico/
    :alt: Number of PyPI downloads


Installation
------------
As usual, mico is available from pypi_, and can be installed using ``pip``::

  pip install mico

.. _pypi: http://pypi.python.org/pypi

Mico just need an AWS key ID and AWS secret key to run. By default mico just
take this variables from the OS environment::

    export AWS_ACCESS_KEY_ID="*foo*"
    export AWS_SECRET_ACCESS_KEY="*bar*"


QuickStart
----------
Mico works using the concept of template. A template is just a python code
(with steroids which we call *libraries*), the template can implements
a number of actions to perform in the cloud. In this example we just create
a new host in AWS and install some packages there.

.. code-block:: python

    from mico.lib.aws import *
    from mico.lib.core import *

    def deploy(*args):
        for host in args:
            instance = ec2_ensure(
                ami = "ami-3d4ff254",
                name = host,
                instance_type = "t1.micro",
                key_name = "root-us-east-virginia",
                security_groups = "sec-test"
            )

            package_ensure("python") # of course :)
            package_ensure("apache")


Once, your template is created, you need to put it into a mico template path
(by default uses ``/etc/mico`` and ``~/.config/mico/``, and the current
working directory.

Then you can just run mico

.. code-block:: bash

    $ mico template:deploy myhost1.mydomain.com myhost2.mydomain.com
    mico:cloud:deploy:create security group: sec-test
    mico:cloud:deploy:create instance: i-4543123
    mico:cloud:deploy:use existent security group: sec-test
    mico:cloud:deploy:create instance: i-2291281


You can see more complex (and useful!) templates in `examples directory`_.

.. _`examples directory`: tree/master/examples

.. raw:: html

  <button class="tpl"><a href="https://github.com/ajdiaz/mico/tree/master/examples">View template
  examples</a></button>




