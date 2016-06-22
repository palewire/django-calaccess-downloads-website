#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from getpass import getpass
from fabric.tasks import Task
from fabric.colors import green
from fabric.api import task, env, local
from boto3 import Session


def require_input(prompt, hide=False):
    """
    Demand input from the user.
    """
    i = None
    while not i:
        if hide:
            i = getpass(prompt.strip()+' ')
        else:
            i = raw_input(prompt.strip()+' ')

        if not i:
            print '  I need this, please.'
    return i


def add_aws_config(setting, value):
    """
    Add an aws configuration (setting name and value) to the config file.
    """
    with open(env.config_file, 'r') as f:
        lines = f.readlines()
    with open(env.config_file, 'w') as f:
        prev_set = False
        for line in lines:
            if 'export {0}='.format(setting.upper()) in line:
                prev_set = True
                f.write('export {0}={1}\n'.format(setting.upper(), value))
            elif len(line) == 0:
                pass
            else:
                f.write(line)

        if not prev_set:
            f.write('export {0}={1}\n'.format(setting.upper(), value))


@task
def configure():
    """
    Create a configuration file that stores AWS configuration that exports
    aws settings into the current environment.
    """
    config = {}

    print('')
    print('AWS configuration')
    print('=================')
    print('')

    # Request data from the user
    config['AWS_ACCESS_KEY_ID'] = require_input(
        'Your AWS access key [Required]:',
        hide=True,
    )
    config['AWS_SECRET_ACCESS_KEY'] = require_input(
        'Your AWS secret key [Required]:',
        hide=True,
    )
    config['key_name'] = raw_input(
        'Your AWS key name [Default: my-key-pair]:'
    ) or 'my-key-pair'
    config['RDS_HOST'] = raw_input('RDS Host [press ENTER (RETURN) to skip]:')
    config['EC2_HOST'] = raw_input('EC2 Host[press ENTER (RETURN) to skip]:')
    config['DB_PASSWORD'] = require_input(
        'Database user password [Required]:',
        hide=True,
    )

    print "Creating .secrets..."
    
    with open(env.config_file, 'w') as f:
        f.write('#!/bin/bash\n\n')

    for k, v in config.iteritems():
        add_aws_config(k, v)

    print('')
    print(green('That\'s it. All set up!'))
    print('Configuration saved in config.yml')
    print('')


def loadconfig():
    """
    Load aws configs into fab env
    """

    if not os.path.isfile(env.config_file):
        configure()

    local('source {0}'.format(env.config_file))

    env.AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    env.AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    env.KEY_NAME = os.getenv('KEY_NAME')
    env.EC2_HOST = os.getenv('EC2_HOST')
    env.RDS_HOST = os.getenv('RDS_HOST')
    env.DB_USER_PASSWORD = os.getenv('DB_PASSWORD')

    env.key_filename = (
        os.path.join(env.key_file_dir, "%s.pem" % env.KEY_NAME),
    )

    env.hosts = [env.EC2_HOST,]
    env.host = env.EC2_HOST
    env.host_string = env.EC2_HOST


class ConfigTask(Task):
    def __init__(self, func, *args, **kwargs):
        super(ConfigTask, self).__init__(*args, **kwargs)
        self.func = func

    def __call__(self):
        self.run()

    def run(self, *args, **kwargs):
        loadconfig()
        return self.func(*args, **kwargs)
