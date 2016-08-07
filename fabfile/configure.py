#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from collections import OrderedDict
import configparser
from fabric.tasks import Task
from fabric.colors import green, cyan
from fabric.api import task, env, sudo
from fabric.operations import put, prompt

#
# Tasks
#


@task
def setconfig(key, value):
    """
    Add or edit a key-value pair in the .env configuration file.
    """
    # Get the existing config
    cp = configparser.SafeConfigParser()
    cp.read(env.config_file)

    # if the config file section is not there, add it
    if not cp.has_section(env.config_section):
        cp.add_section(env.config_section)

    # Set the value provided by the user
    cp.set(env.config_section, key, value)

    # Write to the .env file
    with open(env.config_file, 'wb') as f:
        cp.write(f)


@task
def createconfig():
    """
    Prompt users for settings to be stored in .env file
    """
    # Kick it off
    print('')
    print('Configuration')
    print('=================')
    print('')

    # Request data from the user
    config = OrderedDict()
    config['AWS_ACCESS_KEY_ID'] = prompt('Your AWS access key:')
    config['AWS_SECRET_ACCESS_KEY'] = prompt('Your AWS secret key:')
    config['AWS_REGION_NAME'] = prompt(
        'Your AWS region name:',
        default='us-west-2',
    )
    config['KEY_NAME'] = prompt('Your AWS key name:', default='my-key-pair')
    config['DB_HOST'] = prompt('Database host:', default="localhost")
    config['DB_NAME'] = prompt('Database name:', default='calaccess_website')
    config['DB_USER'] = prompt('Database user:', default=env.app_user)
    config['DB_PASSWORD'] = prompt('Database user password:')
    config['S3_ARCHIVED_DATA_BUCKET'] = prompt(
        'Name of the S3 bucket for archived data:',
        default='django-calaccess-dev-data-archive',
    )
    config['S3_BAKED_CONTENT_BUCKET'] = prompt(
        'Name of the S3 bucket for baked content:',
        default='django-calaccess-dev-baked-content',
    )
    config['EMAIL_USER'] = prompt('E-mail user:')
    config['EMAIL_PASSWORD'] = prompt('E-mail password:')
    config['EC2_HOST'] = prompt('EC2 host:')

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
        print("{}:{}".format(cyan(k), v))


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
    Copy current configurations in local .env file to the ec2 instance.
    """
    # Load settings from the config file
    loadconfig()

    # Push it to the remote environment
    put(env.config_file, env.repo_dir, use_sudo=True)

    # Set the proper file permissions
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
    print "Loading {} configuration settings from {}".format(
        cyan(env.config_section),
        cyan(env.config_file)
    )

    # Open the configuration file
    cp = configparser.SafeConfigParser()
    cp.read(env.config_file)

    # Grad the section we're seeking and uppercase the settings
    d = dict((k.upper(), v) for k, v in cp.items(env.config_section))

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
