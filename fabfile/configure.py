#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import StringIO
import ConfigParser
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


def getconfig():
    """
    Return a dict of the vars currently in the config_file
    """
    # Hack to get around the fact that our .env file lacks a section header,
    # which is a silly requirement of ConfigParser.
    config = StringIO.StringIO()
    config.write('[fabric]\n')
    config.write(open(env.config_file).read())
    config.seek(0, os.SEEK_SET)
    # Parse the configuration
    cp = ConfigParser.ConfigParser()
    cp.readfp(config)
    # Pass it out
    return dict(cp.items("fabric"))


@task
def printconfig():
    """
    Print out the configuration settings for the local environment.
    """
    # Loop through the current configuration
    for k, v in getconfig().items():
        # Print out each setting
        print("{}:{}".format(k, v))


@task
def setconfig(key, value):
    """
    Add or edit a key-value pair in the .env configuration file.
    """
    # Get the existing config
    config = getconfig()

    # Set the value provided by the user
    config[key] = value

    # Create a configure a parser object
    cp = ConfigParser.ConfigParser()
    cp.add_section('fabric')
    for k, v in config.items():
        cp.set("fabric", k, v)

    # Write the object to a virtual file object
    io = StringIO.StringIO()
    cp.write(io)
    s = io.getvalue()

    # Remove the section name from the first line because we don't want it
    s = '\n'.join(io.getvalue().split('\n')[1:-1])

    # Write out the real file
    with open(env.config_file, 'wb') as f:
        f.write(s)

    # Close the virtual file
    io.close()


@task
def configure():
    """
    Initialize AWS configuration, which are stored in the config_file.
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
    config['KEY_NAME'] = raw_input(
        'Your AWS key name [Default: my-key-pair]:'
    ) or 'my-key-pair'
    config['DB_PASSWORD'] = require_input(
        'Database user password [Required]:',
        hide=True,
    )
    config['RDS_HOST'] = raw_input('RDS Host [press ENTER to skip]:')
    config['EC2_HOST'] = raw_input('EC2 Host [press ENTER to skip]:')

    with open(env.config_file, 'w') as f:
        f.write('#!/bin/bash\n\n')

        for k, v in config.iteritems():
            f.write('export {0}={1}\n'.format(k, v))

    print('')
    print(green('That\'s it. All set up!'))
    print('Configuration saved in {0}'.format(env.config_file))
    print('')


def loadconfig():
    """
    Load aws configs into fab env
    """
    if not os.path.isfile(env.config_file):
        configure()

    config = getconfig()

    for k, v in config.iteritems():
        env[k] = v
    
    try:
        env.hosts = [env.EC2_HOST, ]
        env.host = env.EC2_HOST
        env.host_string = env.EC2_HOST
    except AttributeError:
        pass

    try:
        env.key_filename = (
            os.path.join(env.key_file_dir, "%s.pem" % env.KEY_NAME),
        )
    except AttributeError:
        pass

    try:
        env.hosts = [env.EC2_HOST, ]
        env.host = env.EC2_HOST
        env.host_string = env.EC2_HOST
    except AttributeError:
        pass

    try:
        env.key_filename = (
            os.path.join(env.key_file_dir, "%s.pem" % env.key_name),
        )
    except AttributeError:
        pass


class ConfigTask(Task):
    def __init__(self, func, *args, **kwargs):
        super(ConfigTask, self).__init__(*args, **kwargs)
        self.func = func

    def __call__(self):
        self.run()

    def run(self, *args, **kwargs):
        loadconfig()
        return self.func(*args, **kwargs)
