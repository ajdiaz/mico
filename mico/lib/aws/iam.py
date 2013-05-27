#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""The IAM module offers functions to handle AWS users, groups, permissions
and certificates
"""

from os import environ as os_environ
from fnmatch import fnmatch
from boto.iam.connection import IAMConnection

import mico.output

class IAMTemplateError(Exception):
    """Models a IAM template error."""

def iam_connect(region=None, *args, **kwargs):
    """Helper to connect to Amazon Web Services IAM, using identify provided
    by environment, as also optional region in arguments.

    .. note:: The region parameter is allowed, but do nothing, still here
        for future API compatibility and orthogonality between templates.
    """

    if not os_environ.get("AWS_ACCESS_KEY_ID", None):
        raise IAMTemplateError("Environment variable AWS_ACCESS_KEY_ID is not set.")
    if not os_environ.get("AWS_SECRET_ACCESS_KEY", None):
        raise IAMTemplateError("Environment variable AWS_SECRET_ACCESS_KEY is not set.")

    connection = IAMConnection(
            os_environ.get("AWS_ACCESS_KEY_ID"),
            os_environ.get("AWS_SECRET_ACCESS_KEY"),
            *args, **kwargs
    )

    return connection

def iam_cert_exists(filter_expr='*'):
    """Returns the list of server certificates which match with specified
    filter expression passed as argument or None if none match.
    """
    conn = iam_connect()

    # Ohh Holy shit!!!
    meta = conn.get_all_server_certs()['list_server_certificates_response']['list_server_certificates_result']['server_certificate_metadata_list']
    _x = filter(lambda x:fnmatch(x["server_certificate_name"], filter_expr), meta)
    if _x:
        return _x[0]
    else:
        return _x

def iam_cert_ensure(name, public, private, chain=None, path=None):
    """Ensure that the certificate which name is passed as argument exists,
    if not and content is provided, upload the new cert.

    :type name: str
    :param name: the name of the certificate

    :type content: str
    :param name: the content (PEM) of the certificate
    """
    _obj = iam_cert_exists(name)

    if _obj:
        mico.output.info("use existent certificate: %s" % name)
        return _obj

    conn = iam_connect()
    return conn.upload_server_cert(name, public, private, chain, path)


