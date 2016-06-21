#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from os.path import expanduser, join

from fabric.colors import green
from fabric.api import env, local, task, sudo

from configure import loadconfig, add_aws_config
from configure import ConfigTask
from chef import installchef, rendernodejson, cook
from amazon import createrds, createserver, createkeypair
from app import pipinstall, manage, migrate, collectstatic, rmpyc
from dev import rs

import aws_config

env.user = 'ubuntu'
env.chef = '/usr/bin/chef-solo -c solo.rb -j node.json'
env.app_user = 'ccdc'
env.project_dir = '/apps/calaccess/repo/cacivicdata/'
env.activate = 'source /apps/calaccess/bin/activate'
env.AWS_REGION = 'us-west-2'
env.key_file_dir = expanduser('~/.ec2/')

try:
    env.key_filename = (
        join(env.key_file_dir, "%s.pem" % env.key_name),
    )
except AttributeError:
    pass


@task
def ec2bootstrap():
    """
    Install chef and use it to fully install the application on
    an Amazon EC2 instance.
    """
    # Fire up a new server
    id, env.EC2_HOST = createserver()

    # Add the new server's host to the configuration file
    add_aws_config('EC2_HOST', env.EC2_HOST)
    
    print "- Waiting 60 seconds before logging in to configure machine"
    time.sleep(60)

    env.hosts = [env.EC2_HOST,]
    env.host = env.EC2_HOST
    env.host_string = env.EC2_HOST

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


@task
def rdsbootstrap():
    """
    Install chef and use it to fully install the database on
    an Amazon RDS instance.
    """
    # Fire up a new server
    # host = createrds()
    host = 'calaccessraw-95.ccfcfvva9ujy.us-west-2.rds.amazonaws.com'

    # Add the new server's host to the configuration file
    add_aws_config('RDS_HOST', host)

    print(green("Success!"))


@task(task_class=ConfigTask)
def ssh():
    """
    Log into the EC2 instance using SSH.
    """
    local("ssh %s@%s -i %s" % (env.user, env.EC2_HOST, env.key_filename[0]))


__all__ = (
    'loadconfig',
    'createrds',
    'createserver',
    'createkeypair',
    'installchef',
    'pipinstall',
    'rendernodejson',
    'cook',
    'manage',
    'migrate',
    'ssh',
    'collectstatic',
    'ec2bootstrap',
    'rdsbootstrap',
    'rs',
)
