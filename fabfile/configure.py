#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from getpass import getpass
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


def add_aws_config(setting, value):
    """
    Add an aws configuration (setting name and value) to the fab env.
    """
    config_file = 'fabfile/aws_config.py'

    if not os.path.isfile(config_file):
        print "Creating aws_config.py"
        with open(config_file, 'w') as f:
            f.write('from fabric.api import env\n\n')
            f.write("env.{0}='{1}'\n".format(setting, value))
    else:
        with open(config_file, 'r') as f:
            lines = f.readlines()
        with open(config_file, 'w') as f:
            for line in lines:
                prev_set = False
                if 'env.{}='.format(setting) in line:
                    prev_set = True
                    f.write("env.{0}='{1}'\n".format(setting, value))
                elif len(line) == 0:
                    pass
                else:
                    f.write(line)

            if not prev_set:
                f.write("env.{0}='{1}'\n".format(setting, value))


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


class ConfigTask(Task):
    def __init__(self, func, *args, **kwargs):
        super(ConfigTask, self).__init__(*args, **kwargs)
        self.func = func

    def __call__(self):
        self.run()

    def run(self, *args, **kwargs):
        loadconfig()
        return self.func(*args, **kwargs)
