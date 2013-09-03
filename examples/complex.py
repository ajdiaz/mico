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

    for arg in args:
        create_security(arg)
        create_instance(arg)

        install_nginx(arg)
        install_uwsgi(arg)
        install_python(arg)

        create_users(arg)
        configure_sudoers(arg)

        install_global_pip_packages(arg)
        create_virtualenv(arg)
        start_services(arg)


def create_security(args):
    "Create security groups required for the environment."

    sg_frontend = sg_ensure(
            name="frontend",
            description='frontend security group',
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

    return sg_frontend


def create_instance(arg):
    "Create EBS instance for nosy."

    instance = ec2_ensure(
            ami="ami-10314d79",
            name=arg,
            instance_type="t1.micro",
            user_data=USERDATA % (arg, "%s.example.com" % arg, ),
            key_name="root-us-east-virginia",
            security_groups=["frontend"],
            placement="us-east-1a"
    )

# UNUSED
#    xvdf=ebs_ensure(
#        size=8,
#        zone="us-east-1a",
#        volume_type="standard",
#        instance=instance,
#        device="/dev/sdf",
#    )

    return instance


def install_nginx(arg):
    "Install nginx host."

    with mode_sudo():
        package_ensure("nginx-full")
        service_ensure_boot("nginx")


def install_uwsgi(args):
    "Install the uwsgi components into the system."

    with mode_sudo():
        package_ensure("uwsgi")
        package_ensure("uwsgi-infrastructure-plugins")
        package_ensure("uwsgi-plugin-python")


def install_python(args):
    "Install python environment."

    with mode_sudo():
        package_ensure("python")
        package_ensure("python-virtualenv")
        package_ensure("python-pip")


def create_users(args):
    "Create users for host."

    with mode_sudo():
        user_ensure("ajdiaz")
        group_user_add("sudo", "ajdiaz")
        ssh_authorize("ajdiaz",
            "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDX0Ila4UIQkgYRCTeHGzXkZbqYEpwwDlUDDM3oM4j2/hkrd9AY5p/ug921TpN4qi5pooSRwcD5ZiWZNqzPfEefl4A+3pGVfObN3NNUbc0Iry/T6MRdmnWB3LQxc2R45UOhVjLTuCKWRNLyZ1A7sIp7yrBt36BHoSoL40AIBbdEp37oSgubCI953UGNIN70BGAF/Cm0SW5f47NqDM2N2Fz/LA6Zf3NYXqYRzkOkpHxJ10DUvaAXoLiFVQPEGVdgwQJpIUdGZYkhPbgs5yBhBU5y2BLABJb/b1Yt3Yl6qSuBNOPP4oIMYjkUWXHu81hYJe68GpBwWN1AwGv3g7LeFOcx near.to")


def configure_sudoers(args):
    "Configure sudoers file."
    with mode_sudo():
        file_content(
            src="data/sudoers.tpl",
            dst="/etc/sudoers2",
        )


def install_global_pip_packages(args):
    "Install pip packages for host."
    PIP_PACKAGES = ["redis", "bottle"]

    for package in PIP_PACKAGES:
        sudo("pip install --upgrade %s" % package)


def create_virtualenv(args):
    "Create virtualenv for host."
    with mode_sudo():
        dir_ensure("/srv/app/src")
        dir_ensure("/srv/app/env")
    sudo("virtualenv /srv/app/env")


def start_services(args):
    "Start boot services if not running."
    service_ensure("nginx")
    service_reload("nginx")

    service_ensure("uwsgi")
    service_restart("uwsgi")

    service_ensure_boot("uwsgi")


