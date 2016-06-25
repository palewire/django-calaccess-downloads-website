#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from os.path import expanduser
from fabric.colors import green
from fabric.api import env, task, sudo
from configure import (
    setconfig,
    createconfig,
    loadconfig,
    printconfig,
    printenv
)
from chef import installchef, rendernodejson, cook
from amazon import createrds, createserver, createkey
from app import pipinstall, manage, migrate, collectstatic, rmpyc
from dev import rs, pull, ssh

env.user = 'ubuntu'
env.chef = '/usr/bin/chef-solo -c solo.rb -j node.json'
env.app_user = 'ccdc'
env.project_dir = '/apps/calaccess/repo/cacivicdata/'
env.activate = 'source /apps/calaccess/bin/activate'
env.AWS_REGION = 'us-west-2'
env.key_file_dir = expanduser('~/.ec2/')
env.config_file = '.env'


@task
def ec2bootstrap(block_gb_size=100, instance_type='c3.large',
                 ami='ami-978dd9a7'):
    """
    Install chef and use it to fully install the application on
    an Amazon EC2 instance.
    """
    # Fire up a new server
    id, env.EC2_HOST = createserver(block_gb_size, instance_type, ami)
    # Add the new server's host to the configuration file
    setconfig('EC2_HOST', env.EC2_HOST)

    print "- Waiting 60 seconds before logging in to configure machine"
    time.sleep(60)

    rendernodejson()
    # Install chef and run it
    installchef()
    cook()

    # source secrets in activate script
    sudo("echo 'source /apps/calaccess/.secrets' >> /apps/calaccess/bin/activate")

    # Fire up the Django project
    migrate()
    collectstatic()

    # Done deal
    print(green("Success!"))
    print "Visit the app at %s" % env.EC2_HOST


__all__ = (
    'setconfig',
    'createconfig',
    'loadconfig',
    'createrds',
    'createserver',
    'createkey',
    'installchef',
    'pipinstall',
    'printconfig',
    'rendernodejson',
    'cook',
    'manage',
    'migrate',
    'printenv',
    'ssh',
    'collectstatic',
    'ec2bootstrap',
    'rdsbootstrap',
    'rmpyc',
    'rs',
    'pull',
)
