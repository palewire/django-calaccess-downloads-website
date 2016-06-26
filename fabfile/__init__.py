#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from fabric.api import env

from amazon import createrds, createec2, createkey
from app import pipinstall, manage, migrate, collectstatic, rmpyc, pull
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

env.user = 'ubuntu'
env.chef = '/usr/bin/chef-solo -c solo.rb -j node.json'
env.app_user = 'ccdc'
env.app_group = 'ccdc'
env.branch = 'master'
env.app_dir = '/apps/calaccess/'
env.repo_dir = os.path.join(env.app_dir, 'repo/')
env.project_dir = os.path.join(env.repo_dir, 'cacivicdata/')
env.activate = 'source /apps/calaccess/bin/activate'
env.AWS_REGION = 'us-west-2'
env.key_file_dir = os.path.expanduser('~/.ec2/')
env.config_file = '.env'
env.connection_attempts = 15

__all__ = (
    'bootstrap',
    'copyconfig',
    'setconfig',
    'createconfig',
    'loadconfig',
    'createrds',
    'createec2',
    'createkey',
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
