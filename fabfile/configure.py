#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from os.path import expanduser
from getpass import getpass
import yaml
from fabric.tasks import Task
from fabric.colors import green
from fabric.api import task, env
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


@task
def configure():
    """
    Create a configuration file that stores your credentials to a secret file.
    """
    config = {}

    print('')
    print('AWS configuration')
    print('=================')
    print('')

    # Request data from the user
    config['key_name'] = require_input(
        'EC2 Key Pair name [Required]:'
    )
    config['AWS_REGION'] = raw_input(
        "Target AWS region [Default: us-west-2]:"
    ) or 'us-west-2'

    # Write it to a YAML file
    config_file = open('./config.yml', 'w')
    config_file.write(yaml.dump(config, default_flow_style=False))
    config_file.close()

    print('')
    print(green('That\'s it. All set up!'))
    print('Configuration saved in config.yml')
    print('')


def loadconfig():
    """
    Load aws configs into fab env (prompt if necessary)
    """
    creds = Session().get_credentials()

    if creds:
        env.AWS_ACCESS_KEY_ID = creds.access_key
        env.AWS_SECRET_ACCESS_KEY = creds.secret_key
    else:
        env.AWS_ACCESS_KEY_ID = require_input(
            'Your AWS access key [Required]:',
            hide=True
        )
        env.AWS_SECRET_ACCESS_KEY = require_input(
            'Your AWS access key [Required]:',
            hide=True
        )
    
    env.DB_USER_PASSWORD = os.getenv('DB_PASSWORD') or require_input(
            'Password for RDS instance database [Required]:',
            hide=True
        )

    env.key_name = config['key_name']
    env.key_filename = (expanduser("~/.ec2/%s.pem" % env.key_name),)
    env.AWS_REGION = config['AWS_REGION']


class ConfigTask(Task):
    def __init__(self, func, *args, **kwargs):
        super(ConfigTask, self).__init__(*args, **kwargs)
        self.func = func

    def __call__(self):
        self.run()

    def run(self, *args, **kwargs):
        loadconfig()
        return self.func(*args, **kwargs)
