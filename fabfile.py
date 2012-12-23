from fabric.api import *
import aws, os

@task
def check_credentials():
    """
    Ensure that AWS API credentials exist
    """
    if not aws.has_credentials():
        access_key_id = prompt('Access Key ID?')
        secret_access_key = prompt('Secret Access Key?')
        aws.save_credentials(access_key_id, secret_access_key)

@task
def make_vpc(vpc_name='midkemia'):
    """
    Make a VPC - by default the vpc_name is 'midkemia'
    """
    check_credentials()
    bastion_hosts = aws.make_vpc(vpc_name)
    for host in bastion_hosts:
        connect_script(host)

def connect_script(node):
    filename = 'connect_' + node.name
    command = "ssh -i %s -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no %s@%s\n"
    command = command % (node.ssh_key, node.ssh_user, node.public_ip)

    with open(filename, 'w') as script:
        script.write('#!/bin/sh\n')
        script.write(command)

    os.chmod(filename, 0755)
    print "Connect to [%s] instance using ./%s" % (node.name, filename)

