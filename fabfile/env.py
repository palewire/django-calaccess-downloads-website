#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from fabric.api import env, task


# Server credentials
env.user = 'ubuntu'
env.key_file_dir = os.path.expanduser('~/.ec2/')

# Applications user
env.app_user = 'ccdc'
env.app_group = 'ccdc'
env.app_dir = '/apps/calaccess/'
env.activate = 'source {}'.format(
    os.path.join(env.app_dir, "bin", "activate")
)

# Git repository
env.repo = "california-civic-data-coalition/django-calaccess-downloads-website"
env.repo_dir = os.path.join(env.app_dir, 'repo/')

# Extras
env.connection_attempts = 15

# Configuration file
env.base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
env.config_file = os.path.join(env.base_dir, ".env")
os.environ.setdefault("CALACCESS_WEBSITE_ENV", "DEV")
env.config_section = os.getenv('CALACCESS_WEBSITE_ENV').upper()


@task
def dev():
    """
    Operate on the development environment.
    """
    env.config_section = "DEV"


@task
def prod():
    """
    Operate on the production environment.
    """
    env.config_section = "PROD"
