#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from fabric.api import env

from amazon import createrds, createec2, createkey, copydb, copys3
from app import (
    deploy,
    pipinstall,
    manage,
    migrate,
    collectstatic,
    rmpyc,
    pull
)
from dev import rs, ssh
from chef import bootstrap, installchef, rendernodejson, cook
from configure import (
    setconfig,
    copyconfig,
    createconfig,
    loadconfig,
    printconfig,
    printenv
)

# Server credentials
env.user = 'ubuntu'
env.key_file_dir = os.path.expanduser('~/.ec2/')
env.config_file = '.env'

# Application data
env.app_user = 'ccdc'
env.app_group = 'ccdc'
env.repo = "california-civic-data-coalition/django-calaccess-downloads-website"
env.branch = 'master'
env.app_dir = '/apps/calaccess/'
env.repo_dir = os.path.join(env.app_dir, 'repo/')
env.activate = 'source {}bin/activate'.format(env.app_dir)

# Extras
env.chef = '/usr/bin/chef-solo -c solo.rb -j node.json'
env.connection_attempts = 15
# default to configuring DEV environment
os.environ.setdefault("CALACCESS_WEBSITE_ENV", "DEV")

__all__ = (
    'bootstrap',
    'copyconfig',
    'deploy',
    'setconfig',
    'createconfig',
    'loadconfig',
    'createrds',
    'createec2',
    'createkey',
    'copydb',
    'copys3',
    'ec2bootstrap',
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
    'rmpyc',
    'rs',
    'pull',
)
