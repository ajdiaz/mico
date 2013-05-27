===========================================
Mico: a monkey driven cloud management tool
===========================================

Mico is a tool-toy to manage a number of hosts deployed in cloud services
(currently only support Amazon AWS), and also allows you to deploy new hosts
with specified template or create autoscaling groups and manage them easily.

Installation
------------
As usual, mico is available from pypi_, and can be installed using ``pip``
or ``easy_install``::

  pip install mico

Or::

  easy_install mico

.. _pypi: http://pypi.python.org/pypi

Configure Mico
--------------

Mico just need an AWS key ID and AWS secret key to run. By default mico just
take this variables from the OS environment::

    export AWS_ACCESS_KEY_ID="*foo*"
    export AWS_SECRET_ACCESS_KEY="*bar*"

Creating templates
------------------

Mico works using the concept of template. A template is just a python code
(with steroids which we call *libraries*), the template can implements
a number of functions. Here are a simple and stupid template (``stupid.py``)

.. code:: python

    def hello():
      print "Hello world!"

    def bye():
      print "Bye cruel world!"

    def hola(args):
      print "Hola %s" % args


Once, your template is created, you need to put it into a mico template path
(by default uses ``/etc/mico`` and ``~/.config/mico/``, and the current
working directory.

Then you can just run mico::

    mico -H my_new_host stupid:hello
    Hello world!

    mico -H my_new_host stupid:bye
    Bye cruel world!

    mico stupid:hola everyone
    Hola everyone

You can see more complex (and useful!) templates in `examples directory`_.

.. _`examples directory`: tree/master/examples


