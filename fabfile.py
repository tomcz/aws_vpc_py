from fabric.api import *
import aws, os, glob, time

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
    Make VPC - by default the vpc_name is 'midkemia'
    """
    check_credentials()
    bastion_hosts = aws.make_vpc(vpc_name)
    for host in bastion_hosts:
        wait_for_ssh_connection(host)
    for host in bastion_hosts:
        connect_script(host)

@task
def delete_vpc(vpc_name='midkemia'):
    """
    Delete VPC - by default the vpc_name is 'midkemia'
    """
    check_credentials()
    aws.delete_vpc(vpc_name)
    for path in glob.glob('connect_*'):
        os.remove(path)

def connect_script(host):
    filename = 'connect_' + host.name
    command = "ssh -i %s -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no %s@%s\n"
    command = command % (host.keyfile, host.user, host.public_ip)

    with open(filename, 'w') as script:
        script.write('#!/bin/sh\n')
        script.write(command)

    os.chmod(filename, 0755)
    print "Connect to [%s] instance using ./%s" % (host.name, filename)

def wait_for_ssh_connection(host):
    with settings(warn_only=True):
        result = check_ssh(host)
        while result.failed:
            print 'Waiting for SSH service ...'
            time.sleep(5)
            result = check_ssh(host)

def check_ssh(host):
    return local('nc -z -v -w 10 %s 22' % host.public_ip)
