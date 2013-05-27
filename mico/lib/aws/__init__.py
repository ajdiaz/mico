#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# vim:fenc=utf-8:

"""The AWS module provides utilites to deploy instances, volumes and other
cool things from Amazon Web Services. To run these services is mandatory to
configure properly the amazon access key and the amazon secret key,
exporting that values via OS environment, using the variables
AWS_ACCESS_KEY_ID and AWS_ACCESS_SECRET_KEY respectively.
"""
from mico.lib.aws.ec2 import *
from mico.lib.aws.r53 import *
from mico.lib.aws.iam import *
