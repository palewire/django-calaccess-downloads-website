#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os.path import expanduser
from fabric.api import env
from configure import (
    setconfig,
    createconfig,
    loadconfig,
    printconfig,
    printenv
)
from chef import installchef, rendernodejson, cook
from amazon import createrds, createserver, createkey, ec2bootstrap
from app import pipinstall, manage, migrate, collectstatic, rmpyc
from dev import rs, pull, ssh

env.user = 'ubuntu'
env.chef = '/usr/bin/chef-solo -c solo.rb -j node.json'
env.app_user = 'ccdc'
env.project_dir = '/apps/calaccess/repo/cacivicdata/'
env.activate = 'source /apps/calaccess/bin/activate'
env.AWS_REGION = 'us-west-2'
env.key_file_dir = expanduser('~/.ec2/')
env.config_file = '.env'


__all__ = (
    'setconfig',
    'createconfig',
    'loadconfig',
    'createrds',
    'createserver',
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
    'ec2bootstrap',
    'rdsbootstrap',
    'rmpyc',
    'rs',
    'pull',
)
