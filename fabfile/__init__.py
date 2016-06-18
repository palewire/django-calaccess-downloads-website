#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

from fabric.colors import green
from fabric.api import env, local, task, sudo
import yaml

from configure import loadconfig
from configure import ConfigTask
from chef import installchef, rendernodejson, cook
from amazon import createrds, createserver, createkeypair
from app import pipinstall, manage, migrate, collectstatic, rmpyc
from dev import rs

env.user = 'ubuntu'
env.chef = '/usr/bin/chef-solo -c solo.rb -j node.json'
env.app_user = 'ccdc'
env.project_dir = '/apps/calaccess/repo/cacivicdata/'
env.activate = 'source /apps/calaccess/bin/activate'
env.AWS_REGION = 'us-west-2'


@task
def ec2bootstrap():
    """
    Install chef and use it to fully install the application on
    an Amazon EC2 instance.
    """
    # Fire up a new server
    id, host = createserver()

    # Add the new server's host name to the configuration file
    config = yaml.load(open('./config.yml', 'rb'))
    config['EC2_HOST'] = str(host)
    config_file = open('./config.yml', 'w')
    config_file.write(yaml.dump(config, default_flow_style=False))
    config_file.close()

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
    print "Visit the app at %s" % host


@task
def rdsbootstrap():
    """
    Install chef and use it to fully install the database on
    an Amazon RDS instance.
    """
    # Fire up a new server
    host = createrds()

    # Add the new server's host name to the configuration file
    config = yaml.load(open('./config.yml', 'rb'))
    config['RDS_HOST'] = str(host)
    config_file = open('./config.yml', 'w')
    config_file.write(yaml.dump(config, default_flow_style=False))
    config_file.close()

    print(green("Success!"))


@task(task_class=ConfigTask)
def ssh():
    """
    Log into the EC2 instance using SSH.
    """
    local("ssh %s@%s -i %s" % (env.user, env.host, env.key_filename[0]))


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
