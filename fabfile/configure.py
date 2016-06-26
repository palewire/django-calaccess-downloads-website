#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import StringIO
import ConfigParser
from getpass import getpass
from fabric.tasks import Task
from fabric.colors import green
from fabric.api import task, env, sudo
from fabric.operations import put

#
# Tasks
#


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
def createconfig():
    """
    Prompt users for settings to be stored in the config_file.
    """
    # Kick it off
    print('')
    print('Configuration')
    print('=================')
    print('')

    # Request data from the user
    config = {}
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

    # Save it to the configuration file
    [setconfig(k, v) for k, v in config.items()]

    # Tell the user they are done
    print('')
    print(green('That\'s it. All set up!'))
    print('Configuration saved in {0}'.format(env.config_file))
    print('')


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
def printenv():
    """
    Print out the Fabric env settings.
    """
    # Load settings from the config file
    loadconfig()
    # Loop through the Fabric env
    for k, v in sorted(env.items()):
        # Print out each setting
        print("{}:{}".format(k, v))


@task
def copyconfig():
    """
    Copy configurations in local dev environment to current ec2 instance.
    """
    # Load settings from the config file
    loadconfig()
    put(env.config_file, env.repo_dir, use_sudo=True)
    sudo('chown {}:{} {}'.format(
        env.app_user,
        env.app_group,
        os.path.join(env.repo_dir, '.env'))
    )


#
# Helpers
#

def getconfig():
    """
    Return a dict of the vars currently in the config_file
    """
    # Hack to get around the fact that our .env file lacks a section header,
    # which is a silly requirement of ConfigParser.
    config = StringIO.StringIO()
    config.write('[fabric]\n')
    if os.path.isfile(env.config_file):
        config.write(open(env.config_file).read())
    config.seek(0, os.SEEK_SET)

    # Parse the configuration
    cp = ConfigParser.ConfigParser()
    cp.readfp(config)

    # Uppercase the settings
    d = dict((k.upper(), v) for k, v in cp.items("fabric"))

    # Pass it out
    return d


def loadconfig():
    """
    Load configuration settings into the Fabric env
    """
    # If the config file doesn't exist, force its creation
    if not os.path.isfile(env.config_file):
        createconfig()

    # Load all of the configuration settings
    config = getconfig()
    for k, v in config.iteritems():
        env[k] = v

    # If there is an EC2_HOST set, patch it onto the Fabric env object
    if hasattr(env, 'EC2_HOST'):
        env.hosts = [env.EC2_HOST]
        env.host = env.EC2_HOST
        env.host_string = env.EC2_HOST

    # If there is a KEY_NAME set, path it onto the Fabric env object
    if hasattr(env, 'KEY_NAME'):
        key_path = os.path.join(env.key_file_dir, "%s.pem" % env.KEY_NAME)
        env.key_filename = (key_path,)


class ConfigTask(Task):
    """
    A custom Fabric @task that loads settings from an external configuration
    file before execution.
    """
    def __init__(self, func, *args, **kwargs):
        super(ConfigTask, self).__init__(*args, **kwargs)
        self.func = func

    def __call__(self):
        self.run()

    def run(self, *args, **kwargs):
        loadconfig()  # <-- the action
        return self.func(*args, **kwargs)


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
            print('  I need this, please.')
    return i
