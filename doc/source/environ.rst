The Environment
---------------

The environment is a global dictionary which is always available in mico
with the keyworkd ``env``. The environment content some information about
the host where mico is working currently and also contain other some useful
things.

The custon environment, available via ``env.custom``, is a dictionary which
contains some variables which are getted from remote host. For example:

.. code-block:: python

  print env.custom.ip_address

Will print the IP address of the remote host.

There is full list of available custom environments:

.. automodule:: mico.environ
    :members:
    :undoc-members:
    :show-inheritance:

