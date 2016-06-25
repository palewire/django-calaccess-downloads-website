#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fabric.api import env
from os.path import expanduser

from amazon import createrds, createec2, createkey
from app import pipinstall, manage, migrate, collectstatic, rmpyc
from dev import rs, pull, ssh
from chef import bootstrap, installchef, rendernodejson, cook
from configure import (
    setconfig,
    createconfig,
    loadconfig,
    printconfig,
    printenv
)

env.user = 'ubuntu'
env.chef = '/usr/bin/chef-solo -c solo.rb -j node.json'
env.app_user = 'ccdc'
env.project_dir = '/apps/calaccess/repo/cacivicdata/'
env.activate = 'source /apps/calaccess/bin/activate'
env.AWS_REGION = 'us-west-2'
env.key_file_dir = expanduser('~/.ec2/')
env.config_file = '.env'
env.connection_attempts = 15

__all__ = (
    'bootstrap',
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
