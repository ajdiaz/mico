from mico.lib.aws import *

USERDATA = """#cloud-config
hostname: %s
fqdn: %s
manage_etc_hosts: true
locale: C
timezone: Europe/Madrid
apt_update: true
apt_upgrade: true
"""


def main(*args):
    for arg in args:
        deploy(arg)


@async
def deploy(host):
    """Generic deploy system for a number of hosts.

    Example::
        deploy('host1', 'host2')
    """

    host, domain = host.split('.', 1) if '.' in host else (host, 'localdomain')

    sg_test = sg_ensure(
        name="sec-test",
        description="security group to test mico",
        rules=[
            sg_rule(
                protocol="tcp",
                source="0.0.0.0/0",
                port="22"
            ),
            sg_rule(
                protocol="tcp",
                source="0.0.0.0/0",
                port="80"
            )
        ]
    )

    instance = ec2_ensure(
        ami="ami-3d4ff254",
        name=host,
        instance_type="t1.micro",
        user_data=USERDATA % (host, "%s.%s" % (host, domain,)),
        key_name="root-us-east-virginia",
        security_groups=[sg_test]
    )

    return instance


