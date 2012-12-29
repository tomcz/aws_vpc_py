from fabric.api import *
import aws, os, glob, time
from termcolor import colored
from mako.template import Template

# EC2 hostnames & IPs keep on changing
env.disable_known_hosts = True

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
        with connection_to_instance(host):
            setup_puppet_standalone()
            apply_manifest('bastion_host', host.user)
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
    command = 'ssh -i %s -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no %s@%s\n'
    command = command % (host.keyfile, host.user, host.public_ip)

    with open(filename, 'w') as script:
        script.write('#!/bin/sh\n')
        script.write(command)

    os.chmod(filename, 0755)
    print colored('Connect to [%s] instance using ./%s' % (host.name, filename), 'cyan')

def connection_to_instance(host):
    wait_for_ssh_connection(host)
    return settings(host_string=host.public_ip, user=host.user, key_filename=host.keyfile)

def wait_for_ssh_connection(host):
    with settings(warn_only=True):
        result = check_ssh(host)
        while result.failed:
            print 'Waiting for SSH service ...'
            time.sleep(5)
            result = check_ssh(host)

def check_ssh(host):
    return local('nc -z -v -w 10 %s 22' % host.public_ip)

def setup_puppet_standalone():
    tarball_name = 'puppet.tar.gz'
    with settings(warn_only=True):
        result = run('puppet --version')
    if result.failed:
        sudo('apt-get -y update')
        sudo('apt-get -y upgrade')
        sudo('apt-get -y install puppet')
    with settings(warn_only=True):
        run('rm -rf puppet')
        local('rm -rf build')
    local('mkdir build')
    local('tar czf build/%s puppet/*' % tarball_name)
    put('build/' + tarball_name, tarball_name)
    run('tar xzf ' + tarball_name)

def apply_manifest(manifest, user):
    variables = {'user': user}
    output_file = 'build/%s.pp' % manifest
    input_file = 'puppet/manifests/%s.pp' % manifest

    content = Template(filename=input_file).render(variables=variables)
    with open(output_file, 'w') as fp:
        fp.write(content)

    puppet_root = '/home/%s/puppet' % user
    command = 'puppet apply --modulepath=%s/modules %s/%s.pp'

    put(output_file, '%s/%s.pp' % (puppet_root, manifest))
    sudo(command % (puppet_root, puppet_root, manifest))
