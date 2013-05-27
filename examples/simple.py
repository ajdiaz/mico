from mico.lib.aws.ec2 import *
from mico.lib.core import *

USERDATA = """
#cloud-config
hostname: %s
fqdn: %s
manage_etc_hosts: true
locale: C
timezone: Europe/Madrid
apt_update: true
apt_upgrade: true
"""

def main(*args):
    "Deploy the entire nosy production environment"

    import pickle
    x = pickle.load(open("/tmp/caca","r"))

    x("a")

